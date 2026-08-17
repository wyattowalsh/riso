# Facts

- This lane may write only under `src/riso/**` and `tests/unit/test_cli/**`.
- This lane must not write `template/files/**`, `template/copier.yml`, `template/hooks/**`, `template/macros/**`, `module_catalog.json.jinja`, `web/**`, `samples/*/render/**`, `samples/*/copier-answers.yml`, or `scripts/ci/**`.
- Agents in this lane do not create branches, worktrees, commits, or pushes unless the human explicitly asks.
- All Python and pytest invocations use `uv run` (e.g. `uv run pytest`, `uv run riso`).
- The maintainer surface stays CLI + skills; a maintainer riso-mcp server is not reintroduced.
- `uv run riso --help` exits successfully and lists the maintainer commands.
- `uv run riso doctor --json` succeeds in a normal dev environment and emits a JSON envelope with `ok`, `command`, `data`, `errors`, and `warnings`.
- `uv run pytest tests/unit/test_cli/ -q` passes.
- The lane owns doctor, validate, copy, update, recopy, diff, variants, catalog, prompts, export, and related template utilities under `src/riso`.
- When work is assigned, the lane prioritizes agent reliability (JSON envelopes, exit codes, path resolution, timeouts), expands unit coverage when behavior changes, and may add or expand CLI commands within owned paths.
- JSON output uses the stable Envelope shape: `ok`, `command`, `data`, `errors`, `warnings`.
- Behavior changes in `src/riso` include matching updates under `tests/unit/test_cli`.
- Copier prompt, hook, macro, or catalog contract gaps are reported as COORD handoffs; this lane does not edit those template contract surfaces to fix CLI bugs.
- The lane may read `template/` and `samples/` for introspection and validation without taking write ownership of those trees.
- Default verification is `uv run pytest tests/unit/test_cli/ -q`, `uv run riso doctor --json`, and `uv run riso catalog|prompts|variants` when those commands are touched; `just quality` only if broader maintainer Python surfaces are affected or requested.
- The generated project Typer CLI under `template/files/python` is out of scope (PY lane).
- Secrets are never committed, printed, or persisted by this lane.
- `uv.lock` and `pnpm-lock.yaml` are never hand-edited.
