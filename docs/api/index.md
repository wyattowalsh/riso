# API Reference

The API reference is generated via `sphinx.ext.autodoc` with full type hint support.

```bash
uv sync --group docs
uv run sphinx-build docs docs/_build
```

Rendered projects inherit this configuration so `autodoc` can scan packages in
`apps/` and `packages/` automatically when present.

## Modules

::::{grid} 2
:gutter: 3

:::{grid-item-card} Riso CLI
:link: ../tools/riso-cli
:link-type: doc

Agent-native Typer CLI for template introspection, validation, and Copier operations.

Use `uv run riso --help` for the command reference.
:::

:::{grid-item-card} Template Utilities
:link: template/index
:link-type: doc

Template discovery, metadata, and path resolution utilities.
:::

:::{grid-item-card} Scripts
:link: scripts
:link-type: doc

Command-line scripts and automation utilities.
:::

::::

```{note}
The maintainer `riso-mcp` server was removed in v1.2.0. See
{doc}`../guides/mcp-to-cli-migration` for migration guidance.
```
