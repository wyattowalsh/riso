#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAMPLES_DIR="${REPO_ROOT}/samples"
COPIER_CMD=${COPIER_CMD:-copier}

log() {
  printf "[render-samples] %s\n" "$*" >&2
}

run_module_smoke_tests() {
  local variant="$1"
  local answers_file="$2"
  local destination="$3"
  local log_path
  log_path="$(dirname "${answers_file}")/smoke-results.json"

  python3 - "$variant" "$answers_file" "$destination" "$log_path" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

variant, answers_path, destination, log_path = sys.argv[1:5]
answers_file = Path(answers_path)
destination_path = Path(destination)


def load_answers(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def collect_modules(config: dict[str, str]) -> list[dict[str, object]]:
    api_tracks = config.get("api_tracks", "").lower()
    docs_site = config.get("docs_site", "").lower()

    docs_command: list[str] | None
    docs_reason = "Documentation module disabled."
    if docs_site == "fumadocs":
        docs_command = ["pnpm", "--filter", "docs-fumadocs", "build"]
        docs_reason = "Fumadocs build command configured."
    elif docs_site == "sphinx-shibuya":
        docs_command = ["uv", "run", "make", "linkcheck"]
        docs_reason = "Sphinx Shibuya link check configured."
    elif docs_site == "docusaurus":
        docs_command = ["pnpm", "--filter", "docs-docusaurus", "build"]
        docs_reason = "Docusaurus build command configured."
    else:
        docs_command = None
        docs_reason = "Documentation scaffolding skipped (`docs_site=none`)."

    modules: list[dict[str, object]] = [
        {
            "name": "cli",
            "enabled": config.get("cli_module", "").lower() == "enabled",
            "command": ["uv", "run", "pytest", "tests/test_cli.py"],
        },
        {
            "name": "api_python",
            "enabled": api_tracks in {"python", "python+node"},
            "command": ["uv", "run", "pytest", "tests/test_api_fastapi.py"],
        },
        {
            "name": "api_node",
            "enabled": api_tracks in {"node", "python+node"},
            "command": ["pnpm", "--filter", "api-node", "test"],
        },
        {
            "name": "mcp_module",
            "enabled": config.get("mcp_module", "").lower() == "enabled",
            "command": None,
            "skip_reason": "MCP smoke tests pending implementation.",
        },
        {
            "name": "docs_site",
            "enabled": docs_site != "none",
            "command": docs_command,
            "skip_reason": docs_reason,
        },
        {
            "name": "shared_logic",
            "enabled": config.get("shared_logic", "").lower() == "enabled",
            "command": None,
            "skip_reason": "Shared logic smoke tests pending implementation.",
        },
    ]
    return modules


def run_command(cmd: list[str]) -> tuple[str, dict[str, object]]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=destination_path,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        return "error", {
            "command": cmd,
            "reason": str(exc),
        }
    except subprocess.CalledProcessError as exc:
        return "failed", {
            "command": cmd,
            "returncode": exc.returncode,
            "stdout": exc.stdout,
            "stderr": exc.stderr,
        }
    else:
        return "passed", {
            "command": cmd,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }


config = load_answers(answers_file)
modules = collect_modules(config)
results: list[dict[str, object]] = []

for module in modules:
    if not module.get("enabled"):
        results.append(
            {
                "name": module["name"],
                "status": "skipped",
                "reason": "Module disabled in prompt answers.",
            }
        )
        continue
    command = module.get("command")
    if not command:
        results.append(
            {
                "name": module["name"],
                "status": "skipped",
                "reason": module.get("skip_reason", "No smoke command configured."),
            }
        )
        continue
    status, payload = run_command(command)
    entry = {"name": module["name"], "status": status}
    entry.update(payload)
    results.append(entry)

summary = {"variant": variant, "results": results}
Path(log_path).write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary))
PY
}

write_render_metadata() {
  local variant="$1"
  local answers_file="$2"
  local destination="$3"
  local duration="$4"

  python3 - "$variant" "$answers_file" "$destination" "$duration" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

variant, answers_path, destination, duration_seconds = sys.argv[1:5]
answers_file = Path(answers_path)
variant_dir = answers_file.parent


def load_answers(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


answers = load_answers(answers_file)
duration = float(duration_seconds)
completed_at = datetime.now(tz=timezone.utc).isoformat()

metadata = {
    "variant": variant,
    "answers_file": str(answers_file),
    "destination": str(Path(destination)),
    "completed_at": completed_at,
    "render_duration_seconds": duration,
    "project_layout": answers.get("project_layout", "single-package"),
    "modules": {
        "cli_module": answers.get("cli_module", "disabled"),
        "api_tracks": answers.get("api_tracks", "none"),
        "mcp_module": answers.get("mcp_module", "disabled"),
        "docs_site": answers.get("docs_site", "starter-guide"),
        "shared_logic": answers.get("shared_logic", "disabled"),
    },
}

doc_publish = {
    "site": answers.get("docs_site", "starter-guide"),
    "status": "pending",
    "recorded_at": completed_at,
}

write_json(variant_dir / "metadata.json", metadata)
write_json(variant_dir / "doc-publish.json", doc_publish)
PY
}

render_variant() {
  local variant="$1"
  local answers_file="$2"
  local destination="$3"
  local start_ts
  local end_ts
  local duration

  log "Rendering variant '${variant}' using answers '${answers_file}'"
  start_ts=$(date +%s)
  rm -rf "${destination}"
  mkdir -p "$(dirname "${destination}")"
  ${COPIER_CMD} copy \
    --data-file "${answers_file}" \
    --force \
    "${REPO_ROOT}" \
    "${destination}"
  if ! run_module_smoke_tests "${variant}" "${answers_file}" "${destination}"; then
    log "Smoke tests encountered issues for variant '${variant}' (continuing)."
  fi
  end_ts=$(date +%s)
  duration=$((end_ts - start_ts))
  write_render_metadata "${variant}" "${answers_file}" "${destination}" "${duration}"
}

render_default() {
  render_variant "default" "${SAMPLES_DIR}/default/copier-answers.yml" "${SAMPLES_DIR}/default/render"
  "${REPO_ROOT}/scripts/ci/run_baseline_quickstart.py"
}

usage() {
  cat <<EOF
Usage: $0 [--variant NAME --answers FILE]

Without arguments the script renders the default sample. When --variant and
--answers are provided it renders just that combination.
EOF
}

main() {
  if [[ $# -eq 0 ]]; then
    log "Starting sample render orchestrator (defaults)"
    render_default
    log "Sample rendering complete"
    exit 0
  fi

  local variant=""
  local answers=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --variant)
        variant="$2"
        shift 2
        ;;
      --answers)
        answers="$2"
        shift 2
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        log "Unknown argument: $1"
        usage
        exit 1
        ;;
    esac
  done

  if [[ -z "${variant}" || -z "${answers}" ]]; then
    log "--variant and --answers are required when arguments are supplied"
    usage
    exit 1
  fi

  render_variant "${variant}" "${answers}" "${SAMPLES_DIR}/${variant}/render"
}

main "$@"
