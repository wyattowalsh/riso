# No Legacy Answer Policy

Riso release readiness uses only canonical component-first answer keys.

## Removed Keys

- `api_tracks`
- `api_language`
- `docs_site`
- `mcp_language`
- `saas_starter_module`

## Required Behavior

- Do not convert removed keys into canonical keys.
- Do not add hidden aliases, fallbacks, migrations, or dual-path behavior.
- Reject removed keys with a clear validation error.
- Keep active docs, examples, samples, web presets, and MCP payloads canonical.
- Allow removed-key strings only in negative tests and release notes that explain
  rejection behavior.
