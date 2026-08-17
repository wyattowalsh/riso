"""Root pytest hooks.

Ignore Copier templates and JS/TS specs when a hook passes mixed paths
to ``pytest`` (idle-gate matches ``test_`` in any dirty filename).
"""

from __future__ import annotations

from pathlib import Path

_SKIP_SUFFIXES = {".jinja", ".ts", ".tsx", ".js", ".jsx"}


def _skip_non_python_test_path(path: Path) -> bool:
    suffixes = path.suffixes
    return path.suffix in _SKIP_SUFFIXES or (
        len(suffixes) >= 2 and "".join(suffixes[-2:]) == ".py.jinja"
    )


def _normalize_cli_args(args: list[str] | tuple[str, ...]) -> list[str]:
    """Split newline-joined paths and drop Copier/JS specs."""
    expanded: list[str] = []
    for arg in args:
        text = str(arg)
        parts = (
            text.splitlines() if ("\n" in text and not Path(text).exists()) else [text]
        )
        for part in parts:
            if part and not _skip_non_python_test_path(Path(part)):
                expanded.append(part)
    return expanded


def pytest_configure(config: object) -> None:
    """Drop non-Python idle-gate args before xdist fans out (else 0 items)."""
    raw_args = getattr(config, "args", None)
    params = getattr(config, "invocation_params", None)
    param_args = getattr(params, "args", None)
    if raw_args:
        kept = _normalize_cli_args(raw_args)
        if kept != list(raw_args):
            config.args = kept
    if param_args:
        kept_params = tuple(_normalize_cli_args(param_args))
        if kept_params != tuple(param_args):
            try:
                object.__setattr__(params, "args", kept_params)
            except (AttributeError, TypeError):
                pass


def pytest_ignore_collect(collection_path: Path, config: object) -> bool | None:
    """Skip non-Python test-like files so collection of real tests continues."""
    del config
    if _skip_non_python_test_path(collection_path):
        return True
    return None
