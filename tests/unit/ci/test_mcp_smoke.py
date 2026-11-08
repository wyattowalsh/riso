"""Execute the official renderer's API and MCP smoke checks."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.ci.record_module_success import (
    ModuleSuccessRecorder,
    smoke_payload_to_results,
)

ROOT = Path(__file__).resolve().parents[3]
RENDER_SAMPLES = ROOT / "scripts" / "render-samples.sh"
CHECKS = ("typecheck", "build", "test", "lint")
NAMES = tuple(f"mcp_typescript_{check}" for check in CHECKS)
PYTHON_SMOKE = "mcp_python_test"
QUALITY_COMMAND = [
    "uv",
    "run",
    "--group",
    "quality",
    "--group",
    "test",
    "task",
    "quality",
]
PYTHON_COMMAND = [
    "uv",
    "run",
    "--group",
    "mcp",
    "--group",
    "test",
    "pytest",
    "tests/test_mcp.py",
]
PYTHON_FILES = ("pyproject.toml", "tests/test_mcp.py")
NESTED_PYTHON_FILES = tuple(f"python/{path}" for path in PYTHON_FILES)
BASE_ANSWERS = {
    "mcp_module": "enabled",
    "mcp_languages": ["typescript"],
    "cli_module": "disabled",
    "api_module": "disabled",
    "docs_module": "disabled",
    "shared_logic": "disabled",
    "quality_profile": "strict",
}


@pytest.fixture(name="smoke_source")
def _smoke_source():
    """Load the actual Python program embedded in the shell smoke function."""
    text = RENDER_SAMPLES.read_text(encoding="utf-8")
    function = text.split("run_module_smoke_tests() {", 1)[1]
    return function.split("<<'PY'\n", 1)[1].split("\nPY\n}", 1)[0]


@pytest.fixture(name="run_smoke")
def _run_smoke(tmp_path, monkeypatch, smoke_source):
    """Run the real smoke entry point against isolated generated-project fixtures."""

    def run(
        override=None,
        *,
        bootstrap=None,
        workspace=True,
        dependencies=True,
        python_files=(),
    ):
        destination = tmp_path / "render"
        destination.mkdir(exist_ok=True)
        if workspace:
            (destination / "package.json").write_text('{"private":true}\n')
            (destination / "pnpm-workspace.yaml").write_text(
                "packages:\n  - node/mcp\n"
            )
            package = destination / "node" / "mcp"
            package.mkdir(parents=True, exist_ok=True)
            (package / "package.json").write_text('{"name":"@test/mcp-server"}\n')
        if dependencies:
            (destination / "node_modules").mkdir(exist_ok=True)
        for name in python_files:
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        if bootstrap is not None:
            status_file = destination / ".riso" / "bootstrap-status.json"
            status_file.parent.mkdir(exist_ok=True)
            status_file.write_text(json.dumps(bootstrap))
        answers = tmp_path / "copier-answers.yml"
        answers.write_text(yaml.safe_dump({**BASE_ANSWERS, **(override or {})}))
        log = tmp_path / "smoke-results.json"
        monkeypatch.setattr(
            sys,
            "argv",
            ["smoke", "mcp-test", str(answers), str(destination), str(log), str(ROOT)],
        )
        namespace = {"__name__": "__main__"}
        with pytest.raises(SystemExit) as stopped:
            # Execute only repository-owned smoke code; no shell render/install is run.
            exec(  # pylint: disable=exec-used
                compile(smoke_source, str(RENDER_SAMPLES), "exec"), namespace
            )
        return json.loads(log.read_text()), stopped.value.code, namespace, destination

    return run


def _success(command, **_kwargs):
    """Return a successful subprocess result without installing dependencies."""
    return subprocess.CompletedProcess(command, 0, stdout="passed", stderr="")


def test_typescript_collects_and_runs_all_four_checks(run_smoke, monkeypatch):
    """Enabled TypeScript emits per-command proof from the generated root."""
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs["cwd"], "VIRTUAL_ENV" in kwargs["env"]))
        return _success(command)

    monkeypatch.setattr(subprocess, "run", runner)
    payload, code, _namespace, destination = run_smoke()
    assert code == 0
    assert [command for command, _cwd, _venv in calls] == [
        ["pnpm", "--filter", "./node/mcp", "--fail-if-no-match", "run", check]
        for check in CHECKS
    ]
    assert all(cwd == destination and not venv for _command, cwd, venv in calls)
    assert all(payload["modules"][name]["status"] == "passed" for name in NAMES)
    assert payload["modules"]["mcp_module"]["status"] == "skipped"
    assert "Go and Rust" in payload["modules"]["mcp_module"]["reason"]
    assert payload["modules"][PYTHON_SMOKE]["status"] == "skipped"


@pytest.mark.parametrize(
    ("project_path", "python_files"),
    [("python", NESTED_PYTHON_FILES), (".", PYTHON_FILES)],
)
def test_python_runs_shipped_suite_with_dependency_groups(
    run_smoke, monkeypatch, project_path, python_files
):
    """Run the selected suite from either supported rendered Python layout."""
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs["cwd"], "VIRTUAL_ENV" in kwargs["env"]))
        return _success(command)

    monkeypatch.setenv("VIRTUAL_ENV", "/maintainer/test-fixture")
    monkeypatch.setattr(subprocess, "run", runner)
    payload, code, _namespace, destination = run_smoke(
        {"mcp_languages": "python, rust"},
        workspace=False,
        dependencies=False,
        python_files=python_files,
    )
    assert code == 0
    assert calls == [
        (PYTHON_COMMAND, destination / project_path, False),
        (QUALITY_COMMAND, destination / project_path, False),
    ]
    assert payload["modules"][PYTHON_SMOKE]["status"] == "passed"
    assert all(payload["modules"][name]["status"] == "skipped" for name in NAMES)


@pytest.mark.parametrize(
    "features",
    [
        {"api_features": ["graphql", "websocket"]},
        {"graphql_api_module": "enabled", "websocket_module": "enabled"},
    ],
)
def test_python_api_runs_selected_advanced_suites(run_smoke, monkeypatch, features):
    """A selected feature runs its tests with the dependency group it needs."""
    calls = []

    def runner(command, **_kwargs):
        calls.append(command)
        return _success(command)

    monkeypatch.setattr(subprocess, "run", runner)
    payload, code, _namespace, _destination = run_smoke(
        {
            "api_module": "enabled",
            "api_languages": ["python"],
            "mcp_module": "disabled",
            **features,
        },
        workspace=False,
        dependencies=False,
        python_files=("python/pyproject.toml",),
    )

    assert code == 0
    assert payload["modules"]["api_python"]["status"] == "passed"
    assert len(calls) == 2
    assert calls[1] == QUALITY_COMMAND
    command = calls[0]
    pytest_index = command.index("pytest")
    dependency_groups = set(command[3:pytest_index:2])
    assert {"graphql_api", "websocket"} <= dependency_groups
    assert command[pytest_index + 1 :] == [
        "tests/api/",
        "tests/graphql/",
        "tests/websocket/",
    ]


@pytest.mark.parametrize(
    ("python_files", "bootstrap", "reason"),
    [
        ((), None, "no rendered Python project"),
        (("python/pyproject.toml",), None, "tests/test_mcp.py was not rendered"),
        (
            NESTED_PYTHON_FILES,
            {"python_bootstrap": {"status": "error", "reason": "setup failed"}},
            "setup failed",
        ),
    ],
)
def test_selected_python_mcp_reports_missing_inputs_as_errors(
    run_smoke, monkeypatch, python_files, bootstrap, reason
):
    """Missing scaffold and bootstrap failure stop the gate before uv runs."""

    def runner(command, **_kwargs):
        if command == QUALITY_COMMAND:
            return _success(command)
        pytest.fail("Python MCP smoke executed after a failed preflight")

    monkeypatch.setattr(subprocess, "run", runner)
    payload, code, _namespace, _destination = run_smoke(
        {"mcp_languages": ["python"]},
        bootstrap=bootstrap,
        python_files=python_files,
    )
    assert code == 1
    entry = payload["modules"][PYTHON_SMOKE]
    assert entry["status"] == "error"
    assert reason in entry["reason"]


@pytest.mark.parametrize("returncode", [1, 5])
def test_python_failed_or_uncollected_suite_fails_smoke(
    run_smoke, monkeypatch, returncode
):
    """Pytest failures and empty collections keep their exit status in evidence."""

    def runner(command, **_kwargs):
        if command == QUALITY_COMMAND:
            return _success(command)
        assert command == PYTHON_COMMAND
        raise subprocess.CalledProcessError(returncode, command, stderr="pytest failed")

    monkeypatch.setattr(subprocess, "run", runner)
    payload, code, _namespace, _destination = run_smoke(
        {"mcp_languages": ["python"]}, python_files=NESTED_PYTHON_FILES
    )
    assert code == 1
    entry = payload["modules"][PYTHON_SMOKE]
    assert entry["status"] == "failed"
    assert entry["returncode"] == returncode
    assert entry["stderr"] == "pytest failed"


def test_strict_quality_smoke_uses_the_sample_profile_and_propagates_failure(
    run_smoke, monkeypatch
):
    """Ambient settings cannot turn a strict sample into a standard run."""
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs["env"]["QUALITY_PROFILE"]))
        if command == ["make", "quality"]:
            raise subprocess.CalledProcessError(1, command, stderr="strict lint failed")
        return _success(command)

    monkeypatch.setenv("QUALITY_PROFILE", "standard")
    monkeypatch.setattr(subprocess, "run", runner)
    payload, code, _namespace, _destination = run_smoke(
        {"mcp_module": "disabled"},
        python_files=("python/pyproject.toml", "python/justfile", "python/Makefile"),
    )

    assert calls == [
        (["just", "quality"], "strict"),
        (["make", "quality"], "strict"),
        (QUALITY_COMMAND, "strict"),
    ]
    assert code == 1
    assert payload["modules"]["quality_just"]["status"] == "passed"
    assert payload["modules"]["quality_uv_task"]["status"] == "passed"
    assert payload["modules"]["quality_make"]["stderr"] == "strict lint failed"


@pytest.mark.parametrize("failed_check", CHECKS)
def test_each_check_failure_fails_the_smoke_result(
    run_smoke, monkeypatch, failed_check
):
    """Failures retain their actual return code and cannot become skipped/success."""

    def runner(command, **_kwargs):
        if command[-1] == failed_check:
            raise subprocess.CalledProcessError(
                7, command, output="failed", stderr="detail"
            )
        return _success(command)

    monkeypatch.setattr(subprocess, "run", runner)
    payload, code, _namespace, _destination = run_smoke()
    assert code == 1
    for check in CHECKS:
        entry = payload["modules"][f"mcp_typescript_{check}"]
        assert entry["status"] == ("failed" if check == failed_check else "passed")
        if check == failed_check:
            assert entry["returncode"] == 7
            assert entry["stderr"] == "detail"


def test_node_bootstrap_error_is_not_skipped_without_dependencies(
    run_smoke, monkeypatch
):
    """Dependency bootstrap failure blocks every enabled MCP check before execution."""
    calls = []

    def runner(command, **_kwargs):
        calls.append(command)
        return _success(command)

    monkeypatch.setattr(subprocess, "run", runner)
    payload, code, _namespace, _destination = run_smoke(
        bootstrap={"node_bootstrap": {"status": "error", "reason": "setup failed"}},
        dependencies=False,
    )
    assert code == 1
    assert not calls
    assert all(
        payload["modules"][name] == {"status": "error", "reason": "setup failed"}
        for name in NAMES
    )


def test_missing_workspace_is_attempted_and_failed(run_smoke, monkeypatch):
    """Missing rendered output must not become pnpm's default successful no-match."""
    calls = []

    def runner(command, **_kwargs):
        calls.append(command)
        assert "--fail-if-no-match" in command
        raise subprocess.CalledProcessError(
            1, command, output="", stderr="No projects matched the filters"
        )

    monkeypatch.setattr(subprocess, "run", runner)
    payload, code, _namespace, _destination = run_smoke(
        workspace=False, dependencies=False
    )
    assert code == 1
    assert len(calls) == 4
    assert all(payload["modules"][name]["status"] == "failed" for name in NAMES)


@pytest.mark.parametrize(
    "override",
    [
        {"mcp_module": "disabled"},
        {"mcp_languages": ["rust"]},
        {"mcp_languages": ["go"]},
    ],
)
def test_other_languages_do_not_receive_typescript_qualification(
    run_smoke, monkeypatch, override
):
    """Non-TypeScript variants retain explicit skipped language-scoped results."""
    calls = []

    def runner(command, **_kwargs):
        calls.append(command)
        return _success(command)

    monkeypatch.setattr(subprocess, "run", runner)
    payload, code, _namespace, _destination = run_smoke(override)
    assert code == 0
    assert not calls
    assert all(payload["modules"][name]["status"] == "skipped" for name in NAMES)
    assert payload["modules"][PYTHON_SMOKE]["status"] == "skipped"


def test_language_scoped_results_feed_existing_success_recorder(run_smoke, monkeypatch):
    """Canonical module statuses aggregate without introducing a schema/alias path."""
    monkeypatch.setattr(subprocess, "run", _success)
    payload, code, _namespace, _destination = run_smoke(
        {"mcp_languages": ["typescript", "python", "rust"]},
        python_files=NESTED_PYTHON_FILES,
    )
    assert code == 0
    recorder = ModuleSuccessRecorder()
    recorder.update_from_results("mcp-test", smoke_payload_to_results(payload))
    for name in (*NAMES, PYTHON_SMOKE):
        assert recorder.modules[name].passed == 1
        assert recorder.modules[name].skipped == 0
    assert recorder.modules["mcp_module"].skipped == 1


def test_real_run_command_preserves_subprocess_failure(run_smoke):
    """The actual runner captures a failing process without mocking subprocess.run."""
    _payload, code, namespace, _destination = run_smoke({"mcp_module": "disabled"})
    assert code == 0
    status, payload, duration = namespace["run_command"](
        [
            "uv",
            "run",
            "--no-sync",
            "python",
            "-c",
            "import sys; print('smoke failure', file=sys.stderr); sys.exit(7)",
        ],
        ROOT,
    )
    assert status == "failed"
    assert payload["returncode"] == 7
    assert "smoke failure" in payload["stderr"]
    assert duration >= 0


def test_real_run_command_reports_missing_executable(run_smoke):
    """An unavailable tool is an error and cannot be reported as successful smoke."""
    _payload, code, namespace, destination = run_smoke({"mcp_module": "disabled"})
    assert code == 0
    status, payload, _duration = namespace["run_command"](
        [str(destination / "missing-mcp-smoke-tool")], destination
    )
    assert status == "error"
    assert "reason" in payload
