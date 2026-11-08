"""Regression checks for publishing the exact image that passed the scan."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml
from jinja2 import Environment, FileSystemLoader


TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "template" / "files"
DIGEST = "sha256:" + "a" * 64
SOURCE_IMAGE = f"localhost:5000/riso/api-python@{DIGEST}"


def _workflow(languages: list[str]) -> dict:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_ROOT)))
    rendered = env.get_template(
        ".github/workflows/riso-container-publish.yml.jinja"
    ).render(api_module="enabled", api_languages=languages)
    return yaml.safe_load(rendered)


@pytest.mark.parametrize("languages", [["python"], ["node"], ["python", "node"]])
def test_publish_copies_the_scanned_build_without_rebuilding(
    languages: list[str],
) -> None:
    """Promote the scanned digest and retain its provenance without rebuilding."""
    job = _workflow(languages)["jobs"]["publish-ghcr"]
    steps = job["steps"]
    builds = [
        step
        for step in steps
        if step.get("uses", "").startswith("docker/build-push-action@")
    ]
    assert len(builds) == 1
    build = builds[0]
    assert build["id"] == "build"
    assert build["with"]["push"] is True
    assert "load" not in build["with"]
    assert build["with"]["provenance"] is True
    assert build["with"]["sbom"] is True
    assert build["with"]["tags"] == "${{ steps.tags.outputs.scan_tag }}"

    by_name = {step["name"]: step for step in steps}
    scan = by_name["Run Trivy scan"]
    promote = by_name["Push scanned image"]
    assert scan["with"]["image-ref"] == (
        "registry:5000/${{ steps.tags.outputs.scan_repository }}"
        "@${{ steps.build.outputs.digest }}"
    )
    assert promote["env"]["SOURCE_IMAGE"] == (
        "localhost:5000/${{ steps.tags.outputs.scan_repository }}"
        "@${{ steps.build.outputs.digest }}"
    )
    assert promote["env"]["EXPECTED_DIGEST"] == "${{ steps.build.outputs.digest }}"
    assert "uses" not in promote
    assert {row["name"] for row in job["strategy"]["matrix"]["target"]} == set(
        languages
    )


def test_scan_failures_block_registry_login_and_promotion() -> None:
    """Require a successful scan before registry login and digest promotion."""
    job = _workflow(["python"])["jobs"]["publish-ghcr"]
    steps = job["steps"]
    by_name = {step["name"]: step for step in steps}
    scan = by_name["Run Trivy scan"]
    assert scan["with"]["exit-code"] == "1"
    assert not job.get("continue-on-error", False)
    assert not scan.get("continue-on-error", False)
    names = [step["name"] for step in steps]
    assert names.index("Build image") < names.index("Run Trivy scan")
    assert (
        names.index("Run Trivy scan")
        < names.index("Log in to GitHub Container Registry")
        < names.index("Push scanned image")
    )
    for name in ("Log in to GitHub Container Registry", "Push scanned image"):
        assert by_name[name].get("if", "success()") == "success()"
        assert not by_name[name].get("continue-on-error", False)


def test_ephemeral_registry_is_reachable_from_runner_and_scan_container() -> None:
    """Expose the pinned temporary registry to the builder and scanner."""
    job = _workflow(["python"])["jobs"]["publish-ghcr"]
    registry = job["services"]["registry"]
    assert "@sha256:" in registry["image"]
    assert registry["ports"] == ["5000:5000"]
    by_name = {step["name"]: step for step in job["steps"]}
    setup = by_name["Set up Docker Buildx"]["with"]
    assert setup["driver-opts"] == "network=host"
    assert '[registry."localhost:5000"]' in setup["buildkitd-config-inline"]
    assert "http = true" in setup["buildkitd-config-inline"]
    scan = by_name["Run Trivy scan"]
    assert scan["env"]["TRIVY_IMAGE_SRC"] == "remote"
    assert scan["env"]["TRIVY_INSECURE"] == "true"
    assert scan["with"]["image-ref"].startswith("registry:5000/")


def _run_promotion(
    tmp_path: Path,
    tags: str,
    *,
    reported_digest: str = DIGEST,
    create_status: int = 0,
    inspect_status: int = 0,
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    steps = _workflow(["python"])["jobs"]["publish-ghcr"]["steps"]
    script = next(step["run"] for step in steps if step["name"] == "Push scanned image")
    calls = tmp_path / "docker-calls.txt"
    mock = """
docker() {
    printf '%s\n' "$*" >> "$RISO_TEST_CALLS"
    case "$3" in
        create) return "$RISO_TEST_CREATE_STATUS" ;;
        inspect)
            printf '%s\n' "$RISO_TEST_DIGEST"
            return "$RISO_TEST_INSPECT_STATUS"
            ;;
        *) return 90 ;;
    esac
}
"""
    result = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", mock + script],
        env={
            **os.environ,
            "SOURCE_IMAGE": SOURCE_IMAGE,
            "EXPECTED_DIGEST": DIGEST,
            "IMAGE_TAGS": tags,
            "RISO_TEST_CALLS": str(calls),
            "RISO_TEST_DIGEST": reported_digest,
            "RISO_TEST_CREATE_STATUS": str(create_status),
            "RISO_TEST_INSPECT_STATUS": str(inspect_status),
        },
        capture_output=True,
        text=True,
        check=False,
    )
    return result, calls.read_text().splitlines()


@pytest.mark.parametrize(
    "tags",
    [
        "ghcr.io/owner/api-python:latest,ghcr.io/owner/api-python:commit-sha",
        "ghcr.io/owner/api-python:v1.2.3,ghcr.io/owner/api-python:v1.2,"
        "ghcr.io/owner/api-python:v1",
    ],
)
def test_every_published_tag_receives_the_scanned_digest(
    tmp_path: Path, tags: str
) -> None:
    """Copy each requested tag and verify it resolves to the scanned digest."""
    result, calls = _run_promotion(tmp_path, tags)
    assert result.returncode == 0, result.stderr
    image_tags = tags.split(",")
    assert calls[0].split() == [
        "buildx",
        "imagetools",
        "create",
        "--prefer-index=false",
        *(arg for tag in image_tags for arg in ("--tag", tag)),
        SOURCE_IMAGE,
    ]
    assert len(calls) == len(image_tags) + 1
    for tag, call in zip(image_tags, calls[1:], strict=True):
        assert (
            call == f"buildx imagetools inspect {tag} --format {{{{.Manifest.Digest}}}}"
        )


@pytest.mark.parametrize(
    "overrides,expected_status,expected_calls",
    [
        ({"create_status": 17}, 17, 1),
        ({"inspect_status": 23}, 23, 2),
        ({"reported_digest": "sha256:" + "b" * 64}, 1, 2),
    ],
)
def test_promotion_rejects_copy_inspect_or_digest_failures(
    tmp_path: Path, overrides: dict, expected_status: int, expected_calls: int
) -> None:
    """Fail promotion on copy errors, inspection errors, or a changed digest."""
    result, calls = _run_promotion(
        tmp_path,
        "ghcr.io/owner/api-python:latest,ghcr.io/owner/api-python:commit-sha",
        **overrides,
    )
    assert result.returncode == expected_status
    assert len(calls) == expected_calls


@pytest.mark.parametrize("publish_result", ["success", "failure", "skipped"])
def test_summary_reports_actual_publish_result(
    tmp_path: Path, publish_result: str
) -> None:
    """Report publication success only when the publish job succeeded."""
    steps = _workflow(["python"])["jobs"]["summary"]["steps"]
    summary = tmp_path / "summary.md"
    subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", steps[0]["run"]],
        env={
            **os.environ,
            "PUBLISH_RESULT": publish_result,
            "GITHUB_STEP_SUMMARY": str(summary),
        },
        check=True,
    )
    contents = summary.read_text()
    assert ("✓" in contents) == (publish_result == "success")
    if publish_result != "success":
        assert f"Container publishing result: {publish_result}" in contents
