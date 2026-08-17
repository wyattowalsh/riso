# Handoff: Empty optional dirs still appear when features off

- **Need:** Ensure COORD `_exclude` rules fully omit optional python subtrees when features are disabled so renders do not leave empty `graphql_api/`, `websocket/`, `mcp/`, `docs/`, `release/`, or empty codegen subpackages.
- **Why PY needs it:** In-file dual-gates correctly emit disabled stubs or empty content for optional modules, but empty directories still appear in scratch renders (e.g. `cli-docs` with `api_module=disabled`). That is confusing for consumers and can interact with packaging/discovery.
- **Proposed contract (non-binding):** Audit/tighten `template/copier.yml` `_exclude` lines for `python/src/.../graphql_api`, `websocket`, `python/mcp`, `python/docs`, `python/release`, and codegen paths so they match the same enablement conditions as in-file Jinja.
- **Consuming paths under `template/files/python/`:** all optional surface roots (gated content already PY-correct).
- **Evidence:** Scratch render of `samples/cli-docs` produced empty dirs under `python/src/riso_cli_docs/{graphql_api,websocket}`, `python/mcp`, `python/docs`, `python/release`, while API tests correctly rendered as disabled stubs. `full-stack` correctly materializes websocket + mcp content.
- **Owner:** COORD
