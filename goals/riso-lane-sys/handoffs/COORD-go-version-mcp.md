# COORD handoff: `go_version` when-clause should include MCP

**From:** SYS lane
**To:** COORD
**Priority:** P1

## Problem

In `template/copier.yml`, `go_version` is gated as:

```yaml
when: "{{ 'go' in cli_languages or 'go' in api_languages }}"
```

It does **not** include `'go' in mcp_languages`. Go-MCP-only projects therefore may not prompt for `go_version`, while:

- `samples/go-mcp/copier-answers.yml` still sets `go_version: "1.24"`
- SYS templates under `template/files/go/mcp/` now use `{{ go_version | default('1.22') }}` so renders stay valid with a default

## Requested change (COORD only)

Update the `go_version` `when` to:

```yaml
when: "{{ 'go' in cli_languages or 'go' in api_languages or 'go' in mcp_languages }}"
```

Optionally align MCP default with root default (`1.24`) in docs/help text.

## SYS scope

SYS will **not** edit `template/copier.yml`. Templates already tolerate missing `go_version` via defaults.
