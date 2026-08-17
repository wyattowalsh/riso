# PLATFORM operating checklist

Standing protocol for the Riso maintainer **PLATFORM** lane.

## Exclusive write roots

| Path | Notes |
|------|--------|
| `scripts/ci/**` | CI automation scripts |
| `scripts/render-samples.sh` | Sample render entrypoint (+ closely related) |
| `template/files/quality/**` | Shared quality payload for generated projects |
| `template/files/testing/**` | Shared testing/e2e helpers |
| `samples/*/copier-answers.yml` | Sample answers currency (no invented keys) |
| `samples/metadata/**` | Tool-generated only |
| `.github/workflows/**` | Minimal glue for quality/validate-samples/matrix only |
| `goals/riso-lane-platform/**` | Ops, audit, inbox/outbox |
| `tests/unit/ci/**` | Unit tests for PLATFORM CI scripts |

## Forbidden write paths

- `samples/*/render/**` — regenerate via scripts only
- `template/copier.yml`, `template/hooks/**`, `template/macros/**`
- `template/files/module_catalog.json.jinja`
- `template/files/{python,node,go,rust,frontend,electron,tauri}/**`
- `src/riso/**`, `web/**`
- `uv.lock`, `pnpm-lock.yaml`
- Secrets; unsolicited branches/commits/pushes

## Inbound triggers

1. COORD outbox contract deltas
2. Payload-lane handoffs into `inbox/`
3. CI failures in PLATFORM write roots
4. Any red maintainer CI (investigate; fix only exclusive roots; outbox foreign)

## Ownership router (foreign)

| Path | Owner |
|------|--------|
| copier / hooks / macros / catalog / context | COORD |
| `src/riso/**` | CLI |
| `template/files/python/**` | PY |
| `template/files/node/**` (non-saas) | NODE |
| saas / shadcn product | SAAS |
| go / rust | SYS |
| electron / tauri | DESKTOP |

## Verification matrix

| Condition | Command |
|-----------|---------|
| Touched answers | `uv run riso validate --answers-file samples/<v>/copier-answers.yml --json` |
| Answers changed | `uv run python scripts/ci/render_matrix.py` (full) |
| Quality payload | `uv run python scripts/ci/check_quality_parity.py` |
| `scripts/ci` changed | `uv run pytest tests/unit/ci/` (or narrow) |
| Broad CI Python | `just quality` |
| Context involved | `uv run python scripts/ci/verify_context_sync.py` |
| Agents gates | `uv run python scripts/ci/validate_agents_ecosystem.py` |

## Git hygiene

Do not create branches, worktrees, commits, or pushes unless the human explicitly asks.

## Hard rules

- `uv run` for all Python
- Never invent Copier keys; use COORD outbox / published defaults
- Prefer regeneration over hand-editing renders
