# Handoff: Align hook `api_features` membership with CLI normalize

- **Need:** Optional harden of `template/hooks/pre_gen_project.py::_api_features_enabled` (and/or pre-normalize `api_features` to a token list in context) to match `src/riso/core/generation_gates.normalize_api_features` (comma-split, discard `none`).
- **Why PY needs it:** In-file Jinja still uses `"websocket" in api_features` / `"graphql" in api_features`. For string answers this is substring membership. Hooks derive `websocket_module` / `graphql_api_module` with the same string-`in` logic. Dual-gates in PY are defense-in-depth; stricter list tokens reduce false positives if short tokens ever collide.
- **Proposed contract (non-binding):** COORD updates hook normalize so context exposes list-like `api_features` (or a dedicated `api_features_set`) before render; keep legacy module keys.
- **Consuming paths under `template/files/python/`:** all dual-gated WS/GQL modules and `api/main.py.jinja` / `pyproject.toml.jinja` GraphQL group.
- **Evidence:** Samples use scalar YAML (`api_features: none`, `websocket`, `graphql,websocket`). Hook uses `feature in raw` for strings; CLI `normalize_api_features` is stricter.
- **Owner:** COORD
