#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAMPLES_DIR="${REPO_ROOT}/samples"
COPIER_CMD=${COPIER_CMD:-copier}
COPIER_CMD_ARR=()

log() {
  printf "[render-samples] %s\n" "$*" >&2
}

resolve_copier_cmd() {
  local cmd="${COPIER_CMD:-copier}"
  COPIER_CMD_ARR=()
  if [[ "$cmd" == "copier" ]]; then
    if command -v copier >/dev/null 2>&1; then
      COPIER_CMD=copier
      COPIER_CMD_ARR=(copier)
      return 0
    fi
    if [[ -x "${REPO_ROOT}/.venv/bin/copier" ]]; then
      COPIER_CMD="${REPO_ROOT}/.venv/bin/copier"
      COPIER_CMD_ARR=("${REPO_ROOT}/.venv/bin/copier")
      return 0
    fi
    echo "ERROR: copier not found in PATH or ${REPO_ROOT}/.venv/bin/copier" >&2
    echo "Run: uv sync --group dev (or set COPIER_CMD to an absolute copier path)" >&2
    return 1
  fi
  if [[ "$cmd" == "uv run copier" ]]; then
    COPIER_CMD="uv run copier"
    COPIER_CMD_ARR=(uv run copier)
    return 0
  fi
  if [[ -x "$cmd" ]]; then
    local base
    base="$(basename "$cmd")"
    if [[ "$base" != "copier" ]]; then
      echo "ERROR: COPIER_CMD must resolve to a copier binary (basename: ${base})" >&2
      return 1
    fi
    COPIER_CMD="$cmd"
    COPIER_CMD_ARR=("$cmd")
    return 0
  fi
  echo "ERROR: Invalid COPIER_CMD: $cmd" >&2
  echo "Must be 'copier', 'uv run copier', or an absolute path to the copier binary" >&2
  return 1
}

canonicalize_answers_path() {
  local answers="$1"
  if [[ "${answers}" != /* ]]; then
    answers="${REPO_ROOT}/${answers#./}"
  fi
  uv run python -c "from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())" "${answers}"
}

write_bootstrap_error() {
  local status_file="$1"
  local key="$2"
  local reason="$3"
  uv run python - "${status_file}" "${key}" "${reason}" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
key, reason = sys.argv[2:4]
payload: dict[str, object] = {}
if path.exists():
    payload = json.loads(path.read_text(encoding="utf-8"))
payload[key] = {"status": "error", "reason": reason}
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
PY
}

run_module_smoke_tests() {
  local variant="$1"
  local answers_file="$2"
  local destination="$3"
  local log_path
  log_path="$(dirname "${answers_file}")/smoke-results.json"

  uv run python - "$variant" "$answers_file" "$destination" "$log_path" "${REPO_ROOT}" <<'PY'
import glob
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

variant, answers_path, destination, log_path, repo_root = sys.argv[1:6]
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
from scripts.lib.sphinx_smoke import sphinx_linkcheck_command
answers_file = Path(answers_path)
destination_path = Path(destination)


def load_answers(path: Path) -> dict[str, object]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def as_enabled(value: object) -> bool:
    return str(value or "disabled").lower() == "enabled"


def as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).lower() for item in value]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        return [item.strip().lower() for item in stripped.split(",") if item.strip()]
    return []


def resolve_python_cwd(destination: Path) -> Path | None:
    for candidate in (destination / "python", destination):
        if (candidate / "pyproject.toml").exists():
            return candidate
    return None


def resolve_node_cwd(destination: Path) -> Path | None:
    if (destination / "package.json").exists() or (destination / "pnpm-workspace.yaml").exists():
        return destination
    node_root = destination / "node"
    if (node_root / "package.json").exists() or (node_root / "pnpm-workspace.yaml").exists():
        return node_root
    return None


def collect_modules(config: dict[str, object]) -> list[dict[str, object]]:
    api_enabled = as_enabled(config.get("api_module"))
    api_languages = set(as_list(config.get("api_languages")))
    docs_enabled = as_enabled(config.get("docs_module"))
    docs_framework = str(config.get("docs_framework", "none")).lower()
    quality_profile = str(config.get("quality_profile", "standard")).lower()
    quality_smoke_enabled = quality_profile != "strict"
    python_cwd = resolve_python_cwd(destination_path)
    node_cwd = resolve_node_cwd(destination_path)
    python_project_ready = python_cwd is not None
    node_install_ready = bool(node_cwd and (node_cwd / "node_modules").exists())

    docs_command: list[str] | None
    docs_cwd: Path | None = None
    docs_reason = "Documentation module disabled."
    if docs_enabled and docs_framework == "fumadocs":
        docs_cwd = node_cwd
        fumadocs_pkg = None
        for candidate in (
            destination_path / "node" / "docs" / "fumadocs" / "package.json",
            destination_path / "docs" / "fumadocs" / "package.json",
        ):
            if candidate.exists():
                fumadocs_pkg = candidate
                break
        if fumadocs_pkg and node_install_ready:
            docs_command = ["pnpm", "--filter", "docs-fumadocs", "build"]
            docs_reason = "Fumadocs build command configured."
        else:
            docs_command = None
            docs_reason = "Fumadocs scaffold rendered; run pnpm install before build smoke."
    elif docs_enabled and docs_framework == "sphinx-shibuya":
        docs_cwd = python_cwd
        if python_cwd and (python_cwd / "docs").exists():
            task_runner = str(config.get("task_runner") or "just")
            docs_command = sphinx_linkcheck_command(python_cwd, task_runner)
            docs_reason = "Sphinx Shibuya link check configured."
        else:
            docs_command = None
            docs_reason = "Sphinx scaffold not present for this rendered variant."
    elif docs_enabled and docs_framework == "docusaurus":
        docs_cwd = node_cwd
        docusaurus_pkg = None
        for candidate in (
            destination_path / "node" / "docs" / "docusaurus" / "package.json",
            destination_path / "docs" / "docusaurus" / "package.json",
        ):
            if candidate.exists():
                docusaurus_pkg = candidate
                break
        if docusaurus_pkg and node_install_ready:
            docs_command = ["pnpm", "--filter", "docs-docusaurus", "build"]
            docs_reason = "Docusaurus build command configured."
        else:
            docs_command = None
            docs_reason = "Docusaurus scaffold rendered; run pnpm install before build smoke."
    else:
        docs_command = None
        docs_reason = "Documentation scaffolding skipped (`docs_module=disabled`)."

    api_python_command: list[str] = [
        "uv",
        "run",
        "--group",
        "api_python",
        "--group",
        "api_python_test",
        "--group",
        "test",
    ]
    if as_enabled(config.get("cli_module")):
        api_python_command.extend(["--group", "cli"])
    api_python_command.extend(["pytest", "tests/api/"])

    modules: list[dict[str, object]] = [
        {
            "name": "cli",
            "enabled": as_enabled(config.get("cli_module")) and python_project_ready,
            "command": [
                "uv",
                "run",
                "--group",
                "cli",
                "--group",
                "test",
                "pytest",
                "tests/test_cli*.py",
            ],
            "cwd": str(python_cwd) if python_cwd else None,
            "skip_reason": "CLI module disabled or Python project not rendered.",
        },
        {
            "name": "api_python",
            "enabled": api_enabled and "python" in api_languages and python_project_ready,
            "command": api_python_command,
            "cwd": str(python_cwd) if python_cwd else None,
            "skip_reason": "Python API disabled or Python project not rendered.",
        },
        {
            "name": "api_node",
            "enabled": api_enabled and "node" in api_languages and node_install_ready,
            "command": ["pnpm", "--filter", "api-node", "test"],
            "cwd": str(node_cwd) if node_cwd else None,
            "skip_reason": "Node API disabled or pnpm dependencies not installed.",
        },
        {
            "name": "mcp_module",
            "enabled": as_enabled(config.get("mcp_module")),
            "command": None,
            "skip_reason": "MCP smoke tests pending implementation.",
        },
        {
            "name": "docs",
            "enabled": docs_enabled,
            "command": docs_command,
            "cwd": str(docs_cwd) if docs_cwd else None,
            "skip_reason": docs_reason,
        },
        {
            "name": "shared_logic",
            "enabled": as_enabled(config.get("shared_logic")),
            "command": None,
            "skip_reason": "Shared logic smoke tests pending implementation.",
        },
    ]
    modules.extend(
        [
            {
                "name": "quality_just",
                "enabled": quality_smoke_enabled
                and python_project_ready
                and python_cwd is not None
                and (python_cwd / "justfile").exists(),
                "command": ["just", "quality"],
                "cwd": str(python_cwd),
                "skip_reason": (
                    "Strict quality profile skips render smoke; run `just quality` locally."
                    if not quality_smoke_enabled
                    else "Just quality scaffold not rendered for this variant."
                ),
            },
            {
                "name": "quality_make",
                "enabled": quality_smoke_enabled
                and python_project_ready
                and python_cwd is not None
                and (python_cwd / "Makefile").exists(),
                "command": ["make", "quality"],
                "cwd": str(python_cwd),
                "skip_reason": (
                    "Strict quality profile skips render smoke; run `make quality` locally."
                    if not quality_smoke_enabled
                    else "Python quality scaffold not rendered for this variant."
                ),
            },
            {
                "name": "quality_uv_task",
                "enabled": quality_smoke_enabled and python_project_ready and python_cwd is not None,
                "command": [
                    "uv",
                    "run",
                    "--group",
                    "quality",
                    "--group",
                    "test",
                    "task",
                    "quality",
                ],
                "cwd": str(python_cwd) if python_cwd else None,
                "skip_reason": (
                    "Strict quality profile skips render smoke; run `uv run task quality` locally."
                    if not quality_smoke_enabled
                    else "Python quality scaffold not rendered for this variant."
                ),
            },
        ]
    )
    return modules


def expand_command(cmd: list[str], cwd: Path) -> list[str]:
    expanded: list[str] = []
    for part in cmd:
        if any(marker in part for marker in ("*", "?", "[")):
            matches = sorted(glob.glob(str(cwd / part)))
            if matches:
                expanded.extend(matches)
                continue
        expanded.append(part)
    return expanded


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[str, dict[str, object], float]:
    start_time = time.time()
    workdir = cwd or destination_path
    cmd = expand_command(cmd, workdir)
    child_env = os.environ.copy()
    child_env.pop("VIRTUAL_ENV", None)
    try:
        proc = subprocess.run(
            cmd,
            cwd=workdir,
            check=True,
            capture_output=True,
            text=True,
            env=child_env,
        )
    except FileNotFoundError as exc:
        duration = time.time() - start_time
        return "error", {
            "command": cmd,
            "reason": str(exc),
        }, duration
    except subprocess.CalledProcessError as exc:
        duration = time.time() - start_time
        return "failed", {
            "command": cmd,
            "returncode": exc.returncode,
            "stdout": exc.stdout,
            "stderr": exc.stderr,
        }, duration
    else:
        duration = time.time() - start_time
        return "passed", {
            "command": cmd,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }, duration


config = load_answers(answers_file)
docs_enabled = as_enabled(config.get("docs_module"))
docs_framework = str(config.get("docs_framework", "none")).lower()
modules = collect_modules(config)
results_dict: dict[str, dict[str, object]] = {}

bootstrap_status: dict[str, object] = {}
bootstrap_file = destination_path / ".riso" / "bootstrap-status.json"
if bootstrap_file.exists():
    bootstrap_status = json.loads(bootstrap_file.read_text(encoding="utf-8"))

python_bootstrap = bootstrap_status.get("python_bootstrap", {})
node_bootstrap = bootstrap_status.get("node_bootstrap", {})
python_bootstrap_failed = (
    isinstance(python_bootstrap, dict)
    and str(python_bootstrap.get("status", "")).lower() == "error"
)
node_bootstrap_failed = (
    isinstance(node_bootstrap, dict)
    and str(node_bootstrap.get("status", "")).lower() == "error"
)


def module_needs_python(name: str) -> bool:
    if name in {
        "cli",
        "api_python",
        "quality_just",
        "quality_make",
        "quality_uv_task",
    }:
        return True
    return (
        name == "docs"
        and docs_enabled
        and docs_framework == "sphinx-shibuya"
    )


def module_needs_node(name: str) -> bool:
    if name == "api_node":
        return True
    return (
        name == "docs"
        and docs_enabled
        and docs_framework in {"fumadocs", "docusaurus"}
    )


for module in modules:
    module_name = module["name"]
    if not module.get("enabled"):
        results_dict[module_name] = {
            "status": "skipped",
            "reason": module.get("skip_reason", "Module disabled in prompt answers."),
        }
        continue
    if python_bootstrap_failed and module_needs_python(module_name):
        results_dict[module_name] = {
            "status": "error",
            "reason": str(python_bootstrap.get("reason", "Python bootstrap failed")),
        }
        continue
    if node_bootstrap_failed and module_needs_node(module_name):
        results_dict[module_name] = {
            "status": "error",
            "reason": str(node_bootstrap.get("reason", "Node bootstrap failed")),
        }
        continue
    command = module.get("command")
    module_cwd = Path(module.get("cwd", destination_path))
    if not command:
        results_dict[module_name] = {
            "status": "skipped",
            "reason": module.get("skip_reason", "No smoke command configured."),
        }
        continue
    status, payload, duration = run_command(command, module_cwd)
    entry: dict[str, object] = {"status": status, "duration": round(duration, 2)}
    # Only include command details for failed/error cases to keep output clean
    if status in ("failed", "error"):
        entry.update(payload)
    results_dict[module_name] = entry

timestamp = datetime.now(timezone.utc).isoformat()
summary = {
    "variant": variant,
    "timestamp": timestamp,
    "modules": results_dict,
}
durations_path = destination_path / ".riso" / "quality-durations.json"
if durations_path.exists():
    summary["quality_durations"] = json.loads(durations_path.read_text(encoding="utf-8"))

Path(log_path).write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary))
failures = sum(
    1
    for entry in results_dict.values()
    if str(entry.get("status", "")).lower() in ("failed", "error")
)
sys.exit(1 if failures else 0)
PY
}

write_render_metadata() {
  local variant="$1"
  local answers_file="$2"
  local destination="$3"
  local duration="$4"

  uv run python - "$variant" "$answers_file" "$destination" "$duration" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

variant, answers_path, destination, duration_seconds = sys.argv[1:5]
answers_file = Path(answers_path)
variant_dir = answers_file.parent


def load_answers(path: Path) -> dict[str, object]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


answers = load_answers(answers_file)
docs_enabled = str(answers.get("docs_module", "disabled")).lower() == "enabled"
docs_framework = str(answers.get("docs_framework", "none")).lower()
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
        "api_module": answers.get("api_module", "disabled"),
        "api_languages": answers.get("api_languages", []),
        "mcp_module": answers.get("mcp_module", "disabled"),
        "mcp_languages": answers.get("mcp_languages", []),
        "docs_module": answers.get("docs_module", "disabled"),
        "docs_framework": docs_framework if docs_enabled else "none",
        "shared_logic": answers.get("shared_logic", "disabled"),
    },
}

doc_publish = {
    "framework": docs_framework if docs_enabled else "none",
    "status": "pending",
    "recorded_at": completed_at,
}

# Nested variants (saas-starter/<stack>/) keep catalog metadata.json.
# Dest-smoke timing goes to render-metadata.json for those paths.
if "/" in variant:
    write_json(variant_dir / "render-metadata.json", metadata)
else:
    write_json(variant_dir / "metadata.json", metadata)
write_json(variant_dir / "doc-publish.json", doc_publish)
PY
}

bootstrap_render_dependencies() {
  local destination="$1"
  local answers_file="$2"
  local python_dir=""
  local node_dir=""
  local status_file="${destination}/.riso/bootstrap-status.json"
  local failed=0

  mkdir -p "${destination}/.riso"
  echo '{}' > "${status_file}"

  if [[ -f "${destination}/python/pyproject.toml" ]]; then
    python_dir="${destination}/python"
  elif [[ -f "${destination}/pyproject.toml" ]]; then
    python_dir="${destination}"
  fi

  if [[ -n "${python_dir}" ]]; then
    log "Bootstrapping Python dependencies in ${python_dir}"
    local -a sync_groups=(--group quality --group test)
    if grep -Eq '^cli_module:[[:space:]]*enabled' "${answers_file}"; then
      sync_groups+=(--group cli)
    fi
    if grep -Eq '^api_module:[[:space:]]*enabled' "${answers_file}" \
      && grep -Eq '(^[[:space:]]*-[[:space:]]*python[[:space:]]*$|^api_languages:[[:space:]]*\[.*python)' "${answers_file}"; then
      sync_groups+=(--group api_python --group api_python_test)
    fi
    if ! (cd "${python_dir}" && env -u VIRTUAL_ENV uv sync "${sync_groups[@]}"); then
      log "ERROR: uv sync failed for ${python_dir}"
      write_bootstrap_error "${status_file}" "python_bootstrap" "uv sync failed for ${python_dir}"
      failed=1
    else
      log "Normalizing rendered Python style in ${python_dir}"
      (cd "${python_dir}" && uv run --group quality ruff format . >/dev/null 2>&1) || true
      # Keep setattr-based CLI metadata (B010/B009 break ty on decorator attributes).
      (cd "${python_dir}" && uv run --group quality ruff check --fix --ignore B009,B010 . >/dev/null 2>&1) || true
    fi
  fi

  if [[ -f "${destination}/package.json" || -f "${destination}/pnpm-workspace.yaml" ]]; then
    node_dir="${destination}"
  elif [[ -f "${destination}/node/package.json" || -f "${destination}/node/pnpm-workspace.yaml" ]]; then
    node_dir="${destination}/node"
  fi

  if [[ -n "${node_dir}" ]]; then
    log "Bootstrapping Node dependencies in ${node_dir}"
    if command -v corepack >/dev/null 2>&1; then
      corepack enable >/dev/null 2>&1 || true
    fi
    if ! (cd "${node_dir}" && pnpm install); then
      log "ERROR: pnpm install failed for ${node_dir}"
      write_bootstrap_error "${status_file}" "node_bootstrap" "pnpm install failed for ${node_dir}"
      failed=1
    fi
  fi

  return "${failed}"
}

validate_render_paths() {
  local variant="$1"
  local answers_file="$2"
  local destination="$3"

  if [[ ! "${variant}" =~ ^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$ ]]; then
    log "ERROR: Invalid variant name: ${variant}"
    exit 1
  fi

  if [[ ! -f "${answers_file}" ]]; then
    log "ERROR: Answers file not found: ${answers_file}"
    exit 1
  fi
  if ! uv run python - "${REPO_ROOT}" "${answers_file}" <<'PY'
import sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
answers = Path(sys.argv[2]).resolve()
samples = (repo / "samples").resolve()
if not answers.is_file() or samples not in answers.parents:
    raise SystemExit(1)
PY
  then
    log "ERROR: Answers file must resolve under ${SAMPLES_DIR}: ${answers_file}"
    exit 1
  fi

  if [[ "${destination}" != "${SAMPLES_DIR}/"*"/render" ]]; then
    log "ERROR: Destination must be samples/<variant>/render (got ${destination})"
    exit 1
  fi
}

render_variant() {
  local variant="$1"
  local answers_file="$2"
  local destination="$3"
  local start_ts
  local end_ts
  local duration

  answers_file="$(canonicalize_answers_path "${answers_file}")"
  validate_render_paths "${variant}" "${answers_file}" "${destination}"

  log "Rendering variant '${variant}' using answers '${answers_file}'"
  log "Removing existing render directory: ${destination}"
  start_ts=$(date +%s)
  rm -rf "${destination}"
  mkdir -p "$(dirname "${destination}")"
  resolve_copier_cmd || exit 1
  # Copier tasks do not always export COPIER_ANSWERS; pre_gen fail-closes without it.
  export COPIER_ANSWERS
  COPIER_ANSWERS="$(
    uv run python -c 'import json, sys, yaml; print(json.dumps(yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}))' \
      "${answers_file}"
  )"
  "${COPIER_CMD_ARR[@]}" copy \
    --trust \
    --vcs-ref=HEAD \
    --data-file "${answers_file}" \
    --force \
    "${REPO_ROOT}/template" \
    "${destination}"
  if [[ -f "${destination}/mise.toml" ]] && command -v mise >/dev/null 2>&1; then
    if ! mise trust "${destination}/mise.toml"; then
      log "WARNING: mise trust failed for ${destination}/mise.toml"
    fi
    # Directory-level trust so `just`/`uv` launched from python/ still accept dest mise.toml.
    mise trust "${destination}" >/dev/null 2>&1 || true
  fi
  if ! bootstrap_render_dependencies "${destination}" "${answers_file}"; then
    log "ERROR: bootstrap failed for variant '${variant}'"
    exit 1
  fi
  if ! run_module_smoke_tests "${variant}" "${answers_file}" "${destination}"; then
    log "Smoke tests failed for variant '${variant}'"
    exit 1
  fi
  end_ts=$(date +%s)
  duration=$((end_ts - start_ts))
  write_render_metadata "${variant}" "${answers_file}" "${destination}" "${duration}"
}

render_default() {
  local validate_containers="${1:-false}"
  render_variant "default" "${SAMPLES_DIR}/default/copier-answers.yml" "${SAMPLES_DIR}/default/render"
  if [[ "${validate_containers}" == "true" ]]; then
    log "Validating containers for default sample..."
    uv run python "${REPO_ROOT}/scripts/ci/validate_dockerfiles.py" "${SAMPLES_DIR}/default/render"
  fi
}

usage() {
  cat <<EOF
Usage: $0 [--variant NAME --answers FILE] [--validate-containers]

Without arguments the script renders the default sample. When --variant and
--answers are provided it renders just that combination.

This script deletes the target render directory with rm -rf before copying.
Paths are constrained to samples/<variant>/render under this repository.

Options:
  --validate-containers   Run Dockerfile validation after rendering
EOF
}

main() {
  local validate_containers="false"

  if [[ $# -eq 0 ]]; then
    log "Starting sample render orchestrator (defaults)"
    render_default "${validate_containers}"
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
      --validate-containers)
        validate_containers="true"
        shift
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

  answers="$(canonicalize_answers_path "${answers}")"
  render_variant "${variant}" "${answers}" "${SAMPLES_DIR}/${variant}/render"

  if [[ "${validate_containers}" == "true" ]]; then
    log "Validating containers for variant '${variant}'..."
    uv run python "${REPO_ROOT}/scripts/ci/validate_dockerfiles.py" "${SAMPLES_DIR}/${variant}/render"
  fi
}

main "$@"
