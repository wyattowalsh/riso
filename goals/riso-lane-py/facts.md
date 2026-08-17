# Facts

- This lane may write only under template/files/python/**; all other paths are read-only or forbidden.
- This lane never edits template/copier.yml, template/hooks/**, template/macros/**, or template/files/module_catalog.json.jinja.
- This lane does not edit node/, go/, rust/, frontend/, electron/, tauri/, quality/, testing/, src/riso/, web/, or samples/** to make Python work.
- This lane does not invent new Copier answer keys; missing keys, defaults, when-conditions, or hook rules become COORD handoffs only.
- Execution covers all three intents: baseline health and gate correctness, hardening across PY surfaces, and targeted feature improvements—still only inside template/files/python/**.
- In-scope surfaces under python/ include packaging/quality config, FastAPI api/, Typer cli/, FastMCP mcp/, GraphQL and WebSocket, Sphinx docs, shipped tests, codegen, and release helpers.
- In-file Jinja conditionals under template/files/python/** stay aligned with existing answers (api_module, cli_module, mcp_module, docs_module, docs_framework, quality_profile, task_runner, api_features, language lists, and documented legacy keys).
- Feature-specific payload content is correct when enabled (e.g. API/CLI/MCP/GraphQL/WebSocket/Sphinx docs) and does not break when sibling modules are disabled.
- Python payload follows existing template style: .jinja extensions where required, absolute imports, Python 3.11+ baseline.
- COORD handoffs are written under goals/riso-lane-py/handoffs/ as markdown notes (need, why, proposed contract, consuming python paths) and never applied from this lane.
- Done includes running `uv run python scripts/ci/validate_jinja_templates.py` when available.
- Done includes `uv run riso validate --answers-file <sample> --json` on python-heavy samples (at least samples/api-python; also docs-sphinx, changelog-python, full-stack as relevant).
- Done includes the narrowest maintainer pytest that covers python payload/render behavior when such tests exist.
- samples/*/render/ is never hand-edited; regeneration is only via render scripts and is not required for this lane's standard done bar.
- This lane never hand-edits uv.lock or pnpm-lock.yaml, never commits/prints/persists secrets, uses `uv run` for Python, and does not create branches, worktrees, commits, or pushes unless the human explicitly asks.
- Stated out-of-scope boundaries stay in force: no expansion of write ownership to COORD/PLATFORM/QUAL/other language trees.
