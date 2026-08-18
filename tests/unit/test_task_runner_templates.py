"""Tests for task_runner template artifacts and Copier exclusions."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from jinja2 import Environment, FileSystemLoader, Template

pytestmark = pytest.mark.unit

TEMPLATE_FILES = Path(__file__).resolve().parents[2] / "template" / "files"
COPIER_YML = Path(__file__).resolve().parents[2] / "template" / "copier.yml"

TASK_RUNNER_EXCLUDE_RULES = [
    ("Makefile", "{% if task_runner in ['just', 'none'] %}Makefile{% endif %}"),
    (
        "quality/makefile.quality",
        "{% if task_runner in ['just', 'none'] %}quality/makefile.quality{% endif %}",
    ),
    (
        "python/Makefile",
        "{% if task_runner in ['just', 'none'] %}python/Makefile{% endif %}",
    ),
    ("go/Makefile", "{% if task_runner in ['just', 'none'] %}go/Makefile{% endif %}"),
    (
        "rust/Makefile",
        "{% if task_runner in ['just', 'none'] %}rust/Makefile{% endif %}",
    ),
    ("justfile", "{% if task_runner in ['makefile', 'none'] %}justfile{% endif %}"),
    (
        "quality/justfile.quality",
        "{% if task_runner in ['makefile', 'none'] %}quality/justfile.quality{% endif %}",
    ),
    (
        "python/justfile",
        "{% if task_runner in ['makefile', 'none'] %}python/justfile{% endif %}",
    ),
    (
        "go/justfile",
        "{% if task_runner in ['makefile', 'none'] %}go/justfile{% endif %}",
    ),
    (
        "rust/justfile",
        "{% if task_runner in ['makefile', 'none'] %}rust/justfile{% endif %}",
    ),
]


def _base_context() -> dict[str, object]:
    return {
        "project_name": "Task Runner Test",
        "project_slug": "task-runner-test",
        "package_name": "task_runner_test",
        "project_layout": "single-package",
        "quality_profile": "standard",
        "task_runner": "just",
        "cli_module": "enabled",
        "cli_languages": ["python"],
        "api_module": "disabled",
        "api_languages": ["python"],
        "mcp_module": "disabled",
        "mcp_languages": ["python"],
        "docs_module": "disabled",
        "docs_framework": "none",
        "changelog_module": "disabled",
        "ci_platform": "github-actions",
        "saas_infra_module": "disabled",
        "graphql_api_module": "disabled",
        "websocket_module": "disabled",
        "codegen_module": "disabled",
        "api_features": [],
    }


def _eval_exclude(rule: str, task_runner: str) -> str | None:
    rendered = Template(rule).render(task_runner=task_runner).strip()
    return rendered or None


def _excluded_task_runner_paths(task_runner: str) -> set[str]:
    return {
        path
        for path, rule in TASK_RUNNER_EXCLUDE_RULES
        if _eval_exclude(rule, task_runner) == path
    }


def test_quality_justfile_and_makefile_share_targets() -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FILES), keep_trailing_newline=True
    )
    context = _base_context()
    quality_make = env.get_template("quality/makefile.quality.jinja").render(**context)
    quality_just = env.get_template("quality/justfile.quality.jinja").render(**context)

    for fragment in ("ruff check", "ty check", "pylint", "coverage run", "hooks:"):
        assert fragment in quality_make
        assert fragment in quality_just
    assert "src/$(PACKAGE_NAME)" in quality_make
    assert "src/task_runner_test" in quality_just
    assert "ruff format src/$(PACKAGE_NAME) tests" in quality_make
    assert "ruff format src/task_runner_test tests" in quality_just
    assert 'env("QUALITY_PROFILE"' in quality_just
    assert "uv --directory" in quality_just
    assert "UV_DIR" in quality_make
    assert "typecheck:" in quality_make
    assert "typecheck:" in quality_just


def test_quality_recipes_include_optional_module_groups() -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FILES), keep_trailing_newline=True
    )
    context = _base_context()
    context.update(
        {
            "api_module": "enabled",
            "api_languages": ["python"],
            "api_features": ["graphql", "websocket"],
            "graphql_api_module": "enabled",
            "websocket_module": "enabled",
            "mcp_module": "enabled",
            "mcp_languages": ["python"],
            "codegen_module": "enabled",
        }
    )
    quality_make = env.get_template("quality/makefile.quality.jinja").render(**context)
    quality_just = env.get_template("quality/justfile.quality.jinja").render(**context)
    quality_uv = env.get_template("quality/uv_tasks/quality.py.jinja").render(**context)
    for fragment in (
        "--group graphql_api",
        "--group websocket",
        "--group mcp",
        "--group codegen",
        "--group api_python",
    ):
        assert fragment in quality_make
        assert fragment in quality_just
    assert '"graphql_api"' in quality_uv
    assert '"websocket"' in quality_uv
    assert '"mcp"' in quality_uv
    assert '"codegen"' in quality_uv
    just_src = (TEMPLATE_FILES / "quality" / "justfile.quality.jinja").read_text(
        encoding="utf-8"
    )
    make_src = (TEMPLATE_FILES / "quality" / "makefile.quality.jinja").read_text(
        encoding="utf-8"
    )
    assert "python/coverage.cfg" in just_src
    assert "python/coverage.cfg" in make_src


def test_quality_justfile_skips_python_recipe_without_python_track() -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FILES), keep_trailing_newline=True
    )
    context = _base_context()
    context.update(
        {
            "cli_module": "disabled",
            "cli_languages": [],
            "api_module": "disabled",
            "api_languages": [],
            "mcp_module": "disabled",
            "mcp_languages": [],
            "docs_module": "enabled",
            "docs_framework": "fumadocs",
        }
    )
    quality_just = env.get_template("quality/justfile.quality.jinja").render(**context)
    assert "quality-python:" not in quality_just
    assert "No Python or Node quality track on this dest" in quality_just


def test_root_delegators_reference_quality_modules() -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FILES), keep_trailing_newline=True
    )
    context = _base_context()

    root_make = env.get_template("Makefile.jinja").render(**context)
    root_just = env.get_template("justfile.jinja").render(**context)
    python_make = env.get_template("python/Makefile.jinja").render(**context)
    python_just = env.get_template("python/justfile.jinja").render(**context)

    assert "quality/makefile.quality" in root_make
    assert "quality/justfile.quality" in root_just
    assert "../quality/makefile.quality" in python_make
    assert "../quality/justfile.quality" in python_just


def test_copier_exclude_rules_reference_task_runner() -> None:
    data = yaml.safe_load(COPIER_YML.read_text(encoding="utf-8"))
    excludes = data.get("_exclude", [])
    joined = "\n".join(str(item) for item in excludes)
    assert "task_runner" in joined
    assert "Makefile" in joined
    assert "justfile" in joined


@pytest.mark.parametrize(
    ("task_runner", "excluded", "present"),
    [
        (
            "just",
            {"Makefile", "quality/makefile.quality", "python/Makefile"},
            {"justfile"},
        ),
        (
            "makefile",
            {"justfile", "quality/justfile.quality", "python/justfile"},
            {"Makefile"},
        ),
        ("both", set(), {"justfile", "Makefile"}),
        (
            "none",
            {
                "Makefile",
                "justfile",
                "quality/makefile.quality",
                "quality/justfile.quality",
            },
            set(),
        ),
    ],
)
def test_task_runner_exclude_rules_by_mode(
    task_runner: str, excluded: set[str], present: set[str]
) -> None:
    paths = _excluded_task_runner_paths(task_runner)
    for path in excluded:
        assert path in paths, f"{task_runner}: expected {path} excluded"
    for path in present:
        assert path not in paths, f"{task_runner}: expected {path} kept"


def test_copier_defaults_task_runner_to_just() -> None:
    data = yaml.safe_load(COPIER_YML.read_text(encoding="utf-8"))
    defaults = data.get("_defaults", {})
    prompts = data.get("task_runner", {})
    assert defaults.get("task_runner") == "just"
    assert prompts.get("default") == "just"


def test_package_json_mcp_typescript_is_valid_json() -> None:
    import json

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FILES), keep_trailing_newline=True
    )
    context = {
        **_base_context(),
        "cli_module": "disabled",
        "api_module": "disabled",
        "mcp_module": "enabled",
        "mcp_languages": ["typescript"],
        "docs_module": "disabled",
        "changelog_module": "disabled",
        "saas_infra_module": "disabled",
        "desktop_module": "disabled",
    }
    rendered = env.get_template("package.json.jinja").render(**context)
    payload = json.loads(rendered)
    assert payload["name"] == "task-runner-test"
    assert "node/mcp" in payload["workspaces"]
    assert payload["packageManager"] == "pnpm@9.15.0"


def test_package_json_saas_workspace_when_enabled() -> None:
    import json

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FILES), keep_trailing_newline=True
    )
    context = {
        **_base_context(),
        "cli_module": "disabled",
        "api_module": "disabled",
        "mcp_module": "disabled",
        "docs_module": "disabled",
        "changelog_module": "disabled",
        "saas_infra_module": "enabled",
        "desktop_module": "disabled",
    }
    rendered = env.get_template("package.json.jinja").render(**context)
    payload = json.loads(rendered)
    assert "node/saas" in payload["workspaces"]
    workspace_yaml = env.get_template("pnpm-workspace.yaml.jinja").render(**context)
    assert '- "node/saas"' in workspace_yaml


def test_package_json_electron_workspace_when_electron_vite() -> None:
    import json

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FILES), keep_trailing_newline=True
    )
    context = {
        **_base_context(),
        "cli_module": "disabled",
        "api_module": "disabled",
        "mcp_module": "disabled",
        "docs_module": "disabled",
        "changelog_module": "disabled",
        "saas_infra_module": "disabled",
        "desktop_module": "enabled",
        "desktop_framework": "electron-vite",
    }
    rendered = env.get_template("package.json.jinja").render(**context)
    payload = json.loads(rendered)
    assert "electron" in payload["workspaces"]
    workspace_yaml = env.get_template("pnpm-workspace.yaml.jinja").render(**context)
    assert '- "electron"' in workspace_yaml


def test_package_json_setup_hooks_respects_task_runner_none() -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FILES), keep_trailing_newline=True
    )
    context = {
        **_base_context(),
        "task_runner": "none",
        "changelog_module": "enabled",
        "api_module": "enabled",
        "api_languages": ["node"],
        "docs_module": "disabled",
        "mcp_module": "disabled",
        "saas_infra_module": "disabled",
        "desktop_module": "disabled",
    }
    rendered = env.get_template("package.json.jinja").render(**context)
    assert "uv run pre-commit install --install-hooks" in rendered
    assert "make hooks" not in rendered


def test_quality_task_ty_target_matches_aggregators() -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FILES), keep_trailing_newline=True
    )
    context = _base_context()
    task = env.get_template("python/tasks/quality.py.jinja").render(**context)
    assert '"src/task_runner_test"' in task
