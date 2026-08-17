# Ruff

[Ruff](https://docs.astral.sh/ruff/) is the default Python linter and formatter
in Riso (maintainer repo and rendered projects).

```bash
just lint
uv run ruff check .
uv run ruff format --check .
```

Rendered projects also run Ruff through `just quality` (or `make quality` when
`task_runner` is `makefile` or `both`). Configuration lives in `ruff.toml` /
`[tool.ruff]` — there is no mypy step in this lane.
