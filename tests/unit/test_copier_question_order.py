"""Copier prompt order, CI choice SSOT, and dead `_exclude` scans."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
COPIER_YML = REPO_ROOT / "template" / "copier.yml"
TEMPLATE_FILES = REPO_ROOT / "template" / "files"
PROMPTS_DIR = REPO_ROOT / "template" / "prompts"

_WHEN_STRINGS = re.compile(r"'[^']*'|\"[^\"]*\"")
_WHEN_IDENT = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")
_IF_WRAP = re.compile(
    r"^\{%-?\s*if\b.*?%\}(.*?)\{%-?\s*endif\s*-?%\}$",
    re.DOTALL,
)

DEAD_EXCLUDE_ALLOWLIST = frozenset(
    {
        ".git",
        ".DS_Store",
        ".mise.toml",
    }
)

DEAD_EXCLUDE_FORBIDDEN = (
    "frontend/",
    "electron/electron-vite/",
    "electron/electron-forge/",
    "electron/tauri/",
    "build/",
    "testing/",
    ".github/workflows/template-ci.yml",
    ".github/workflows/quality-matrix.yml",
    "COMPARISON_PAGE.md",
    "python/mkdocs/",
)


def _load_copier() -> dict[object, object]:
    payload = yaml.safe_load(COPIER_YML.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def iter_copier_prompt_keys(data: dict[object, object]) -> list[str]:
    keys: list[str] = []
    for key, value in data.items():
        if not isinstance(key, str) or key.startswith("_"):
            continue
        if isinstance(value, dict) and "type" in value:
            keys.append(key)
    return keys


def prompt_keys_in_when(when: str, prompt_keys: set[str]) -> set[str]:
    stripped = _WHEN_STRINGS.sub(" ", when)
    found = set(_WHEN_IDENT.findall(stripped))
    return found & prompt_keys


def exclude_dest_path(rule: object) -> str | None:
    text = str(rule).strip()
    if not text:
        return None
    match = _IF_WRAP.match(text)
    if match:
        text = match.group(1).strip()
    return text or None


def exclude_static_prefix(rule: object) -> str | None:
    dest = exclude_dest_path(rule)
    if dest is None:
        return None
    parts: list[str] = []
    for part in dest.split("/"):
        if "{{" in part or "{%" in part:
            break
        if part:
            parts.append(part)
    if not parts:
        return None
    return "/".join(parts)


def _template_relatives(files_root: Path) -> set[str]:
    relatives: set[str] = set()
    for path in files_root.rglob("*"):
        rel = path.relative_to(files_root).as_posix()
        relatives.add(rel)
        if rel.endswith(".jinja"):
            relatives.add(rel[: -len(".jinja")])
        parent = Path(rel).parent.as_posix()
        while parent not in {".", ""}:
            relatives.add(parent)
            parent = Path(parent).parent.as_posix()
    return relatives


def test_when_parents_precede_child_prompts() -> None:
    data = _load_copier()
    keys = iter_copier_prompt_keys(data)
    index = {key: pos for pos, key in enumerate(keys)}
    prompt_set = set(keys)
    violations: list[str] = []
    for child in keys:
        spec = data[child]
        assert isinstance(spec, dict)
        when = spec.get("when")
        if not isinstance(when, str):
            continue
        for parent in prompt_keys_in_when(when, prompt_set):
            if index[parent] >= index[child]:
                violations.append(
                    f"{child} when refs {parent} at index {index[parent]} "
                    f">= child index {index[child]}"
                )
    assert violations == []


def test_ci_platform_precedes_python_versions() -> None:
    keys = iter_copier_prompt_keys(_load_copier())
    assert keys.index("ci_platform") < keys.index("python_versions")


def test_go_version_follows_mcp_languages() -> None:
    keys = iter_copier_prompt_keys(_load_copier())
    assert keys.index("mcp_languages") < keys.index("go_version")


def test_copier_yml_has_no_migrations() -> None:
    data = _load_copier()
    assert "_migrations" not in data
    metadata = data["_metadata"]
    assert isinstance(metadata, dict)
    description = str(metadata.get("description", ""))
    assert "`_migrations`" in description
    assert "riso migrate" in description


def test_desktop_framework_is_vite_or_tauri() -> None:
    spec = _load_copier()["desktop_framework"]
    assert isinstance(spec, dict)
    assert spec["choices"] == ["electron-vite", "tauri"]


def test_ci_platform_prompt_choices_match_copier() -> None:
    expected = _load_copier()["ci_platform"]
    assert isinstance(expected, dict)
    choices = expected["choices"]
    for name in ("ci_platform.yml.jinja", "options.yml.jinja"):
        payload = yaml.safe_load((PROMPTS_DIR / name).read_text(encoding="utf-8"))
        assert isinstance(payload, dict)
        prompt = payload["ci_platform"]
        assert isinstance(prompt, dict)
        assert prompt["choices"] == choices


def test_exclude_static_prefix_strips_jinja_segments() -> None:
    rule = (
        "{% if api_module == 'enabled' %}"
        "python/src/{{ package_name }}/websocket/"
        "{% endif %}"
    )
    assert exclude_static_prefix(rule) == "python/src"
    assert exclude_static_prefix(".mise.toml") == ".mise.toml"
    assert exclude_static_prefix("{% if x %}electron/{% endif %}") == "electron"


def test_dead_exclude_static_prefixes_exist_under_template_files() -> None:
    data = _load_copier()
    excludes = data.get("_exclude", [])
    assert isinstance(excludes, list)
    relatives = _template_relatives(TEMPLATE_FILES)
    missing: list[str] = []
    for rule in excludes:
        prefix = exclude_static_prefix(rule)
        if prefix is None or prefix in DEAD_EXCLUDE_ALLOWLIST:
            continue
        dest = exclude_dest_path(rule) or prefix
        if dest.rstrip("/") in {item.rstrip("/") for item in DEAD_EXCLUDE_FORBIDDEN}:
            missing.append(f"forbidden leftover exclude {dest!r}")
            continue
        if prefix not in relatives:
            missing.append(prefix)
    assert missing == []


def test_forbidden_dead_exclude_paths_are_absent() -> None:
    joined = COPIER_YML.read_text(encoding="utf-8")
    for path in DEAD_EXCLUDE_FORBIDDEN:
        assert path not in joined, f"dead exclude {path!r} still present"
    assert "electron-forge" not in joined
    assert '"frontend/"' not in joined


def test_api_features_graphql_websocket_are_python_fastapi_only() -> None:
    data = _load_copier()
    prompt = data["api_features"]
    assert isinstance(prompt, dict)
    assert prompt["when"] == (
        "{{ api_module == 'enabled' and 'python' in api_languages }}"
    )
    help_text = str(prompt["help"])
    assert "Python-only" in help_text
    assert "Strawberry GraphQL" in help_text
    assert "do not scaffold Apollo, async-graphql" in help_text
    assert "GraphQL endpoint (Strawberry/Apollo/async-graphql)" not in help_text

    excludes = data.get("_exclude", [])
    assert isinstance(excludes, list)
    graphql_docs = [
        rule
        for rule in excludes
        if isinstance(rule, str) and "docs/modules/graphql.md" in rule
    ]
    websocket_docs = [
        rule
        for rule in excludes
        if isinstance(rule, str) and "docs/modules/websockets.md" in rule
    ]
    assert graphql_docs == [
        "{% if not (api_module == 'enabled' and 'python' in api_languages "
        "and ('graphql' in api_features or graphql_api_module == 'enabled')) %}"
        "docs/modules/graphql.md{% endif %}"
    ]
    assert websocket_docs == [
        "{% if not (api_module == 'enabled' and 'python' in api_languages "
        "and ('websocket' in api_features or websocket_module == 'enabled')) %}"
        "docs/modules/websockets.md{% endif %}"
    ]
