"""Copier template helpers for Riso.

Provides a thin wrapper around Copier's API plus convenience helpers
for parsing copier.yml, defaults, sample variants, and module catalogs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import json
import ast

from riso.mcp.errors import OperationTimeoutError


@dataclass
class OperationResult:
    """Standardized result for template operations."""

    success: bool
    destination: Path
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable result."""
        return {
            "success": self.success,
            "destination": str(self.destination),
            "message": self.message,
            "metadata": self.metadata,
        }


@dataclass
class ValidationResult:
    """Validation outcome for template answers."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable result."""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_template_path() -> Path:
    """Return the local template path."""
    return (_repo_root() / "template").resolve()


def get_samples_path() -> Path:
    """Return the local samples path."""
    return (_repo_root() / "samples").resolve()


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyYAML is required to load Copier configuration.") from exc
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_copier_config(template_path: Path | None = None) -> dict[str, Any]:
    """Load copier.yml configuration from the template."""
    template_root = template_path or get_template_path()
    for name in ("copier.yml", "copier.yaml"):
        candidate = template_root / name
        if candidate.exists():
            return _load_yaml(candidate)
    raise FileNotFoundError("copier.yml not found")


def get_prompts(template_path: Path | None = None) -> dict[str, Any]:
    """Return prompt definitions from copier.yml.

    Supports both legacy format (prompts: section) and standard copier format
    (questions at top level).
    """
    config = load_copier_config(template_path)

    # Try legacy format first
    if "prompts" in config:
        return config.get("prompts", {}) or {}

    # Standard copier format: questions are top-level keys
    # Filter out special keys and metadata sections
    special_keys = {
        "_min_copier_version",
        "_template",
        "_faq",
        "_answers_file",
        "_metadata",
        "_defaults",
        "_tasks",
        "_jinja_extensions",
        "_envops",
        "_subdirectory",
        "_exclude",
        "_skip_if_exists",
        "exclude",
        "tasks",
        "defaults",
        "metadata",
        "prompts",
    }

    prompts = {}
    for key, value in config.items():
        if key.startswith("_") or key in special_keys:
            continue
        # Questions are dicts with type, help, choices, etc.
        if isinstance(value, dict) and any(
            k in value for k in ("type", "help", "choices", "default", "when")
        ):
            prompts[key] = value

    return prompts


def _has_template_expr(value: Any) -> bool:
    return isinstance(value, str) and "{{" in value and "}}" in value


def _project_slug(name: str) -> str:
    return name.replace(" ", "-").lower()


def _package_name(slug: str) -> str:
    return slug.replace("-", "_")


def get_defaults(
    template_path: Path | None = None,
    project_name: str | None = None,
) -> dict[str, Any]:
    """Return defaults with prompt defaults merged in.

    Template defaults are merged with prompt-level defaults, and
    derived names are computed from project_name when available.

    Supports both legacy format (defaults: section) and standard copier format
    (_defaults: with underscore prefix).
    """
    config = load_copier_config(template_path)
    # Support both legacy (defaults:) and standard (_defaults:) format
    defaults = dict(config.get("defaults", config.get("_defaults", {})) or {})

    # Merge prompt defaults if not already set.
    prompts = get_prompts(template_path)
    for key, prompt in prompts.items():
        if key in defaults:
            continue
        if isinstance(prompt, dict) and "default" in prompt:
            defaults[key] = prompt["default"]

    if project_name:
        defaults["project_name"] = project_name

    # Compute derived defaults if missing or templated.
    name_value = defaults.get("project_name")
    if isinstance(name_value, str) and name_value:
        slug = _project_slug(name_value)
        if "project_slug" not in defaults or _has_template_expr(
            defaults.get("project_slug")
        ):
            defaults["project_slug"] = slug
        if "package_name" not in defaults or _has_template_expr(
            defaults.get("package_name")
        ):
            defaults["package_name"] = _package_name(slug)

    return defaults


def _extract_prompts_from_config(config: dict[str, Any]) -> dict[str, Any]:
    """Extract prompts from a config dict (supports both formats)."""
    # Try legacy format first
    if "prompts" in config:
        return config.get("prompts", {}) or {}

    # Standard copier format: questions are top-level keys
    special_keys = {
        "_min_copier_version",
        "_template",
        "_faq",
        "_answers_file",
        "_metadata",
        "_defaults",
        "_tasks",
        "_jinja_extensions",
        "_envops",
        "_subdirectory",
        "_exclude",
        "_skip_if_exists",
        "exclude",
        "tasks",
        "defaults",
        "metadata",
        "prompts",
    }

    prompts = {}
    for key, value in config.items():
        if key.startswith("_") or key in special_keys:
            continue
        if isinstance(value, dict) and any(
            k in value for k in ("type", "help", "choices", "default", "when")
        ):
            prompts[key] = value

    return prompts


def merge_answers_with_defaults(
    *,
    project_name: str,
    config: dict[str, Any],
    provided_answers: dict[str, Any],
) -> dict[str, Any]:
    """Merge provided answers with template defaults.

    Ensures derived fields are populated consistently.
    """
    # Support both legacy (defaults:) and standard (_defaults:) format
    defaults = dict(config.get("defaults", config.get("_defaults", {})) or {})

    prompts = _extract_prompts_from_config(config)
    for key, prompt in prompts.items():
        if key in defaults:
            continue
        if isinstance(prompt, dict) and "default" in prompt:
            defaults[key] = prompt["default"]

    if project_name:
        defaults["project_name"] = project_name

    name_value = defaults.get("project_name")
    if isinstance(name_value, str) and name_value:
        slug = _project_slug(name_value)
        if "project_slug" not in defaults or _has_template_expr(
            defaults.get("project_slug")
        ):
            defaults["project_slug"] = slug
        if "package_name" not in defaults or _has_template_expr(
            defaults.get("package_name")
        ):
            defaults["package_name"] = _package_name(slug)

    merged = {**defaults, **provided_answers}

    # Recompute derived names if project_name changed and not explicitly set.
    if "project_name" in merged:
        slug = _project_slug(str(merged["project_name"]))
        merged.setdefault("project_slug", slug)
        merged.setdefault("package_name", _package_name(slug))

    return merged


def _render_template(text: str, context: dict[str, Any]) -> str:
    try:
        from jinja2 import Environment, StrictUndefined
    except ImportError:
        return text

    env = Environment(undefined=StrictUndefined, autoescape=False)
    template = env.from_string(text)
    return template.render(**context)


def _safe_eval(expr: str, context: dict[str, Any]) -> bool:
    node = ast.parse(expr, mode="eval")

    def eval_node(n: ast.AST) -> Any:
        if isinstance(n, ast.Expression):
            return eval_node(n.body)
        if isinstance(n, ast.Name):
            return context.get(n.id)
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.List):
            return [eval_node(elt) for elt in n.elts]
        if isinstance(n, ast.Tuple):
            return tuple(eval_node(elt) for elt in n.elts)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not):
            return not eval_node(n.operand)
        if isinstance(n, ast.BoolOp):
            values = [bool(eval_node(value)) for value in n.values]
            if isinstance(n.op, ast.And):
                return all(values)
            if isinstance(n.op, ast.Or):
                return any(values)
        if isinstance(n, ast.Compare):
            left = eval_node(n.left)
            for op, comparator in zip(n.ops, n.comparators):
                right = eval_node(comparator)
                if isinstance(op, ast.Eq):
                    if left != right:
                        return False
                elif isinstance(op, ast.NotEq):
                    if left == right:
                        return False
                elif isinstance(op, ast.In):
                    if left not in right:
                        return False
                elif isinstance(op, ast.NotIn):
                    if left in right:
                        return False
                else:
                    raise ValueError("Unsupported comparison")
            return True
        raise ValueError("Unsupported expression")

    return bool(eval_node(node))


def _evaluate_when(expr: str | None, context: dict[str, Any]) -> bool:
    if not expr:
        return True
    try:
        rendered = _render_template(expr, context).strip()
    except Exception:
        return False
    if rendered == "":
        return False
    if "{{" in rendered and "}}" in rendered:
        rendered = rendered.replace("{{", "").replace("}}", "").strip()
    lowered = rendered.lower()
    if lowered in {"false", "0", "no", "none"}:
        return False
    if lowered in {"true", "1", "yes"}:
        return True
    try:
        return _safe_eval(rendered, context)
    except Exception:
        return False


def validate_answers(
    answers: dict[str, Any],
    template_path: Path | None = None,
    limit_to_answers: bool = False,
) -> ValidationResult:
    """Validate answers against prompt definitions.

    Unknown keys are ignored but reported as warnings.
    """
    prompts = get_prompts(template_path)
    defaults = get_defaults(template_path)

    context = {**defaults, **answers}

    errors: list[str] = []
    warnings: list[str] = []

    # Unknown keys are warnings (not fatal).
    for key in answers:
        if key not in prompts and key not in defaults:
            warnings.append(f"{key}: unknown answer key")

    for key, prompt in prompts.items():
        if limit_to_answers and key not in answers:
            continue
        prompt_def = prompt if isinstance(prompt, dict) else {}
        when_expr = prompt_def.get("when")
        if not _evaluate_when(when_expr, context):
            continue

        has_answer = key in answers
        default_val = defaults.get(key, prompt_def.get("default"))

        if not has_answer:
            if default_val is None:
                errors.append(f"{key}: required")
            continue

        value = answers.get(key)
        prompt_type = prompt_def.get("type")
        if prompt_type:
            if prompt_type == "bool" and not isinstance(value, bool):
                errors.append(f"{key}: expected bool")
            elif prompt_type == "int" and not isinstance(value, int):
                errors.append(f"{key}: expected int")
            elif prompt_type == "float" and not isinstance(value, (int, float)):
                errors.append(f"{key}: expected float")
            elif prompt_type == "str" and not isinstance(value, str):
                errors.append(f"{key}: expected str")
            elif prompt_type in {"yaml", "json"} and not isinstance(
                value, (dict, list)
            ):
                errors.append(f"{key}: expected {prompt_type} structure")

        choices = prompt_def.get("choices")
        if choices:
            choice_list = list(choices.keys()) if isinstance(choices, dict) else choices
            if value not in choice_list:
                errors.append(f"{key}: invalid choice '{value}'")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def list_sample_variants(samples_path: Path | None = None) -> list[dict[str, Any]]:
    """List sample variants with answers and render state."""
    samples_root = samples_path or get_samples_path()
    variants: list[dict[str, Any]] = []

    if not samples_root.exists():
        return variants

    for variant_dir in sorted(
        [p for p in samples_root.iterdir() if p.is_dir() and p.name != "metadata"],
        key=lambda p: p.name,
    ):
        answers_file = variant_dir / "copier-answers.yml"
        render_dir = variant_dir / "render"

        item: dict[str, Any] = {
            "name": variant_dir.name,
            "path": str(variant_dir),
            "has_answers": answers_file.exists(),
            "has_render": render_dir.exists(),
        }

        if answers_file.exists():
            item["answers"] = _load_yaml(answers_file)

        variants.append(item)

    return variants


def load_sample_answers(
    *,
    samples_path: Path | None = None,
    variant: str,
) -> dict[str, Any]:
    """Load answers for a sample variant if available."""
    samples_root = samples_path or get_samples_path()
    answers_file = samples_root / variant / "copier-answers.yml"
    if not answers_file.exists():
        return {}
    return _load_yaml(answers_file)


def get_module_catalog(
    template_path: Path | None = None,
    answers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Load the module catalog and render Jinja placeholders."""
    template_root = template_path or get_template_path()
    catalog_path = template_root / "files" / "shared" / "module_catalog.json.jinja"
    if not catalog_path.exists():
        catalog_path = template_root / "files" / "shared" / "module_catalog.json"
    if not catalog_path.exists():
        return {"modules": [], "error": "module_catalog.json not found"}

    raw = catalog_path.read_text(encoding="utf-8")
    context = get_defaults(template_root)
    if answers:
        context.update(answers)

    rendered = _render_template(raw, context)
    try:
        return json.loads(rendered)
    except json.JSONDecodeError:
        return {"modules": [], "error": "module_catalog.json invalid", "raw": rendered}


def _filter_kwargs(func: Any, kwargs: dict[str, Any]) -> dict[str, Any]:
    try:
        import inspect

        params = inspect.signature(func).parameters
    except Exception:
        return kwargs

    if any(p.kind.name == "VAR_KEYWORD" for p in params.values()):
        return kwargs

    return {key: value for key, value in kwargs.items() if key in params}


def _run_with_timeout(func: Any, timeout: int | None, *args: Any, **kwargs: Any) -> Any:
    if timeout is None:
        return func(*args, **kwargs)

    from concurrent.futures import (
        ThreadPoolExecutor,
        TimeoutError as FutureTimeoutError,
    )

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError as exc:
            raise OperationTimeoutError(
                operation=func.__name__,
                timeout_seconds=timeout,
                details=f"Operation exceeded {timeout}s timeout",
            ) from exc


def run_generator(
    *,
    destination: Path,
    data: dict[str, Any],
    template_path: Path,
    force: bool = False,
    vcs_ref: str | None = None,
    timeout: int | None = None,
) -> OperationResult:
    """Generate a new project using Copier."""
    dest_path = destination.expanduser().resolve()
    if dest_path.exists() and not force:
        raise FileExistsError(
            f"Destination already exists: {dest_path}. Use force to overwrite."
        )

    try:
        from copier import run_copy
    except ModuleNotFoundError as exc:
        raise RuntimeError("Copier is required to generate projects.") from exc

    kwargs = _filter_kwargs(
        run_copy,
        {
            "data": data,
            "vcs_ref": vcs_ref,
            "force": force,
        },
    )

    _run_with_timeout(
        run_copy,
        timeout,
        str(template_path),
        str(dest_path),
        **kwargs,
    )

    return OperationResult(
        success=True,
        destination=dest_path,
        message="Project generated successfully.",
        metadata={},
    )


def run_update(
    *,
    destination: Path,
    template_path: Path,
    skip_answered: bool = True,
    timeout: int | None = None,
) -> OperationResult:
    """Update an existing project using Copier."""
    dest_path = destination.expanduser().resolve()
    if not dest_path.exists():
        raise FileNotFoundError(dest_path)

    try:
        from copier import run_update
    except ModuleNotFoundError as exc:
        raise RuntimeError("Copier is required to update projects.") from exc

    kwargs = _filter_kwargs(
        run_update,
        {
            "skip_answered": skip_answered,
        },
    )

    _run_with_timeout(
        run_update,
        timeout,
        str(dest_path),
        str(template_path),
        **kwargs,
    )

    return OperationResult(
        success=True,
        destination=dest_path,
        message="Project updated successfully.",
        metadata={},
    )


def run_recopy(
    *,
    destination: Path,
    data: dict[str, Any] | None,
    template_path: Path,
    timeout: int | None = None,
) -> OperationResult:
    """Recopy an existing project using Copier."""
    dest_path = destination.expanduser().resolve()
    if not dest_path.exists():
        raise FileNotFoundError(dest_path)

    try:
        from copier import run_recopy
    except ModuleNotFoundError as exc:
        raise RuntimeError("Copier is required to recopy projects.") from exc

    kwargs = _filter_kwargs(
        run_recopy,
        {
            "data": data,
        },
    )

    _run_with_timeout(
        run_recopy,
        timeout,
        str(dest_path),
        str(template_path),
        **kwargs,
    )

    return OperationResult(
        success=True,
        destination=dest_path,
        message="Project regenerated successfully.",
        metadata={},
    )


__all__ = [
    "OperationResult",
    "ValidationResult",
    "get_template_path",
    "get_samples_path",
    "load_copier_config",
    "get_prompts",
    "get_defaults",
    "merge_answers_with_defaults",
    "validate_answers",
    "list_sample_variants",
    "load_sample_answers",
    "get_module_catalog",
    "run_generator",
    "run_update",
    "run_recopy",
]
