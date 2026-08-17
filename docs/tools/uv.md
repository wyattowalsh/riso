# uv

[uv](https://docs.astral.sh/uv/) is the Python package manager for the
maintainer repo and generated projects. Prefix Python commands with `uv run`
(never bare `python` or `pytest`).

```bash
uv sync --group dev --group docs
uv run pytest
uv run riso --help
```

Lockfiles are managed by uv (`uv.lock`). Do not hand-edit them.
