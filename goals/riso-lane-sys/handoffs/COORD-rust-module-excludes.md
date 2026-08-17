# COORD handoff: missing per-module excludes for `rust/cli` and `rust/api`

**From:** SYS lane
**To:** COORD
**Priority:** P2

## Problem

Go trees are excluded per module in `template/copier.yml`:

- `go/cli/` when CLI not go-enabled
- `go/api/` when API not go-enabled
- `go/mcp/` when MCP not go-enabled

Rust only excludes:

- whole `rust/` when no rust language selected
- `rust/mcp/` when MCP not rust-enabled

There is **no** exclude for `rust/cli/` or `rust/api/`. Enabling only rust MCP or only rust API can still ship unused CLI/API source trees under `rust/`.

## Requested change (COORD)

Add exclude rules analogous to Go, e.g.:

```yaml
- "{% if not (cli_module == 'enabled' and 'rust' in cli_languages) %}rust/cli/{% endif %}"
- "{% if not (api_module == 'enabled' and 'rust' in api_languages) %}rust/api/{% endif %}"
```

Validate against monorepo + single-package layouts and workspace member lists in `rust/Cargo.toml.jinja`.

## SYS scope

SYS does not edit `copier.yml`. Root Cargo gates now include `mcp_languages` so MCP-only rust still gets coherent root tooling when the whole tree is present.
