#!/usr/bin/env python3
"""Bump or audit npm dependency pins in Copier template package.json.jinja files.

Uses npm-check-updates (ncu) against fully rendered sample package.json files,
then syncs resolved version ranges back into the matching template jinja sources.

Workflow:
1. Render the representative sample variant (unless --skip-render).
2. Run ``pnpm dlx npm-check-updates`` in the rendered package directory.
3. With ``--apply``, write upgrades to the rendered package.json and sync pins
   into the template jinja file.

Exit codes:
- 0: All surfaces up to date (check mode) or upgrades applied successfully.
- 1: Outdated dependencies found (check mode) or a command failed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SURFACES_CONFIG = REPO_ROOT / "scripts" / "ci" / "npm_surfaces.json"


@dataclass(frozen=True)
class NpmSurface:
    """A template npm surface backed by a rendered sample package.json."""

    name: str
    sample_variant: str
    package_relpath: str
    template_jinja: str


def load_surfaces_config() -> tuple[tuple[str, ...], tuple[NpmSurface, ...]]:
    data = json.loads(SURFACES_CONFIG.read_text(encoding="utf-8"))
    reject = tuple(data.get("ncu_reject", ["eslint"]))
    surfaces = tuple(
        NpmSurface(
            name=item["name"],
            sample_variant=item["sample_variant"],
            package_relpath=item["package_relpath"],
            template_jinja=item["template_jinja"],
        )
        for item in data["surfaces"]
    )
    return reject, surfaces


NCU_REJECT, SURFACES = load_surfaces_config()


def _run(
    cmd: list[str], *, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    print(f"+ {' '.join(cmd)}", flush=True)
    return subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def render_sample(variant: str) -> Path:
    answers = REPO_ROOT / "samples" / variant / "copier-answers.yml"
    if not answers.exists():
        nested = list((REPO_ROOT / "samples").glob(f"**/{variant}/copier-answers.yml"))
        if nested:
            answers = nested[0]
        else:
            raise FileNotFoundError(f"Missing sample answers for variant: {variant}")

    script = REPO_ROOT / "scripts" / "render-samples.sh"
    result = _run(
        [str(script), "--variant", variant, "--answers", str(answers)],
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Failed to render sample variant: {variant}")

    render_root = answers.parent / "render"
    if not render_root.exists():
        raise FileNotFoundError(f"Render output missing: {render_root}")
    return render_root


def run_ncu(package_dir: Path, *, apply: bool) -> tuple[int, str]:
    cmd = [
        "pnpm",
        "dlx",
        "npm-check-updates",
        "--format",
        "group",
        "--reject",
        ",".join(NCU_REJECT),
    ]
    if apply:
        cmd.append("-u")
    result = _run(cmd, cwd=package_dir)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        print(output)
        raise RuntimeError(f"npm-check-updates failed in {package_dir}")
    return result.returncode, output


def load_package_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_dep_versions(package: dict[str, object]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for section in (
        "dependencies",
        "devDependencies",
        "peerDependencies",
        "optionalDependencies",
    ):
        deps = package.get(section)
        if isinstance(deps, dict):
            for name, version in deps.items():
                if isinstance(version, str):
                    versions[name] = version
    return versions


def sync_versions_to_jinja(jinja_path: Path, versions: dict[str, str]) -> list[str]:
    content = jinja_path.read_text(encoding="utf-8")
    updated: list[str] = []

    for name, version in sorted(versions.items()):
        pattern = rf'("{re.escape(name)}"\s*:\s*")([^"]+)(")'
        new_content, count = re.subn(pattern, rf"\g<1>{version}\g<3>", content)
        if count:
            content = new_content
            updated.append(f"{name} -> {version}")

    if updated:
        jinja_path.write_text(content, encoding="utf-8")
    return updated


def process_surface(
    surface: NpmSurface,
    *,
    apply: bool,
    skip_render: bool,
) -> tuple[str, bool, str | None]:
    print(f"\n== {surface.name} ==")
    if not skip_render:
        render_root = render_sample(surface.sample_variant)
    else:
        answers = REPO_ROOT / "samples" / surface.sample_variant / "copier-answers.yml"
        if not answers.exists():
            nested = list(
                (REPO_ROOT / "samples").glob(
                    f"**/{surface.sample_variant}/copier-answers.yml"
                )
            )
            if not nested:
                raise FileNotFoundError(
                    f"Missing sample answers for variant: {surface.sample_variant}"
                )
            answers = nested[0]
        render_root = answers.parent / "render"

    package_json = render_root / surface.package_relpath
    template_jinja = REPO_ROOT / surface.template_jinja
    if not package_json.exists():
        raise FileNotFoundError(f"Rendered package.json missing: {package_json}")
    if not template_jinja.exists():
        raise FileNotFoundError(f"Template jinja missing: {template_jinja}")

    _, ncu_output = run_ncu(package_json.parent, apply=apply)
    if ncu_output.strip():
        print(ncu_output.strip())

    if apply:
        synced = sync_versions_to_jinja(
            template_jinja,
            collect_dep_versions(load_package_json(package_json)),
        )
        if synced:
            print("Synced to template:")
            for line in synced:
                print(f"  - {line}")
        else:
            print("No template pins changed (already aligned).")
        return surface.name, True, None

    outdated = not (
        "No package versions to upgrade" in ncu_output
        or "All dependencies match" in ncu_output
    )
    if outdated:
        print(f"Outdated dependencies detected for {surface.name}.")
    else:
        print(f"{surface.name} is up to date.")
    return surface.name, not outdated, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Upgrade rendered package.json files and sync pins into template jinja.",
    )
    parser.add_argument(
        "--skip-render",
        action="store_true",
        help="Reuse existing samples/*/render output instead of re-rendering.",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        metavar="N",
        help="Run check mode across up to N surfaces concurrently (requires --skip-render).",
    )
    parser.add_argument(
        "--surface",
        action="append",
        choices=[surface.name for surface in SURFACES],
        help="Limit to one or more surfaces (default: all).",
    )
    args = parser.parse_args()

    selected = [s for s in SURFACES if not args.surface or s.name in args.surface]
    all_ok = True

    if args.apply and args.parallel > 1:
        print("ERROR: --apply cannot run with --parallel > 1", file=sys.stderr)
        return 1

    if args.parallel > 1 and not args.skip_render:
        print("ERROR: --parallel requires --skip-render", file=sys.stderr)
        return 1

    if args.parallel > 1 and not args.apply:
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            futures = {
                pool.submit(
                    process_surface,
                    surface,
                    apply=False,
                    skip_render=True,
                ): surface
                for surface in selected
            }
            for future in as_completed(futures):
                surface = futures[future]
                try:
                    _, ok, _ = future.result()
                    all_ok = all_ok and ok
                except (FileNotFoundError, RuntimeError) as exc:
                    print(f"ERROR ({surface.name}): {exc}", file=sys.stderr)
                    return 1
    else:
        for surface in selected:
            try:
                _, ok, _ = process_surface(
                    surface,
                    apply=args.apply,
                    skip_render=args.skip_render,
                )
                all_ok = all_ok and ok
            except (FileNotFoundError, RuntimeError) as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                return 1

    if args.apply:
        print("\nApply complete. Re-render samples and run package builds to verify.")
        return 0

    if not all_ok:
        print(
            "\nSome template npm surfaces are outdated. "
            "Run: uv run python scripts/ci/bump_template_npm_deps.py --apply",
            file=sys.stderr,
        )
        return 1

    print("\nAll template npm surfaces are up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
