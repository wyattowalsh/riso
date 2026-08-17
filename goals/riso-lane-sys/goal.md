# Goal: Riso Lane SYS — Go and Rust template tracks

## Articulated goal

Harden and heavily modernize the **Go and Rust** scaffold trees in the Riso Copier maintainer repo as the **SYS lane** exclusive owner of `template/files/go/**` and `template/files/rust/**`. Deliver equal-effort, independently useful API · CLI · MCP scaffolds (plus task runners and in-tree docs/tests), keep all four Go HTTP frameworks coherent, keep Rust on Actix-web + Clap + Tokio, and route every contract/sample gap to **COORD/PLATFORM handoffs** without editing forbidden paths.

## Shared understanding

Accepted facts: [`facts.md`](./facts.md) (metadata: [`facts.meta.json`](./facts.meta.json)).

Interview provenance: [`interview.json`](./interview.json), [`interview-result.json`](./interview-result.json).

## Execution plan

Primary plan: [`plan.md`](./plan.md) — parallel blueprint with locks, waves, Mermaid DAG, recovery ladder, and agent spawn briefs.

Machine DAG: [`plan.taskgraph.json`](./plan.taskgraph.json).

File-level shards (79 jinja paths): [`plan.fileshards.json`](./plan.fileshards.json).

## Done condition

- Go and Rust templates are coherent for relevant sample/answer combinations; modernization complete under lane roots only.
- Go: shared foundation (API no longer depends on `cli/internal`), all four `go_framework` values (gin/fiber/echo/chi), CLI + MCP + root tooling aligned with `go_version`.
- Rust: fixed Actix/Clap/Tokio stack; gates/MSRV/layout coherent for cli/api/mcp language multiselects; docs/tests match.
- No writes outside `template/files/go/**`, `template/files/rust/**` (goal package docs/handoffs under `goals/riso-lane-sys/**` allowed).
- COORD/PLATFORM handoffs filed for known gaps (`go_version`+mcp, rust samples, rust module excludes, api_features answers, etc.).
- Verification:

```bash
uv run riso validate --answers-file samples/go-api/copier-answers.yml --json
uv run riso validate --answers-file samples/go-cli/copier-answers.yml --json
uv run riso validate --answers-file samples/go-mcp/copier-answers.yml --json
uv run pytest tests/unit/test_go_templates.py -q
uv run python scripts/ci/validate_jinja_templates.py $(find template/files/go template/files/rust -name '*.jinja')
```

- No hand-edits of `samples/*/render/`, lockfiles, or secrets; no git branch/commit/push unless explicitly requested.

## Launch

```text
/goal goals/riso-lane-sys/goal.md
```
