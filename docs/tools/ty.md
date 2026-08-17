# ty

[ty](https://docs.astral.sh/ty/) is Astral's Python type checker and the live
type-check tool in Riso. It replaced mypy in the quality extra, just/make
recipes, and CI.

```bash
just typecheck
uv run ty check scripts template/hooks src
```

Rendered projects configure `[tool.ty]` in `pyproject.toml` and run
`uv run ty check` (or `just typecheck`). Do not restore `mypy.ini` or treat
mypy as the default checker.
