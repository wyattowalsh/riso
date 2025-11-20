# API Reference

The API reference is generated via `autodoc2` and `sphinx.ext.autodoc`.

```bash
uv sync --group docs
uv run sphinx-build docs docs/_build
```

Rendered projects inherit this configuration so `autodoc2` can scan packages in
`apps/` and `packages/` automatically when present.

## Authoring tips

- Keep docstrings NumPy- or Google-style; napoleon is configured for both.
- Prefer explicit `__all__` exports in packages you want surfaced in the index.
- If modules are intentionally excluded (tests, experimental branches), add
  context in the docstring or module comments to clarify why.
- Cross-link functions and CLI entrypoints using the default `:py:func:` role so
  hoverxref tooltips stay rich.
