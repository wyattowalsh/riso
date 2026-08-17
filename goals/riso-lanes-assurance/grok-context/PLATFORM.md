# Lane PLATFORM

## Mission (3 lines)
After W2 join: sync sample answers from COORD outbox keys (never invent keys), full validate loop, full render_matrix.
Own CI scripts, quality/testing template trees, QUAL go tests, rust sample answers if handoff accepted.
Regenerate renders only via official scripts — never hand-edit `samples/*/render/**`.

## Exclusive write roots
- `scripts/ci/**`
- `scripts/render-samples.sh`
- `scripts/hooks/**` (affinity: quality tooling)
- `template/files/quality/**`
- `template/files/testing/**`
- `samples/*/copier-answers.yml`
- `samples/metadata/**`
- `tests/unit/ci/**`
- `tests/unit/test_go_templates.py` (QUAL gate)
- minimal `.github/workflows/**` (only if PLATFORM-owned)
- `goals/riso-lane-platform/**`

## Forbidden roots
- `samples/*/render/**` hand-edits (regenerate only)
- lockfile hand-edits, secrets, `riso-mcp`
- COORD contract trees (`copier.yml`, hooks, macros, catalog, prompts, context)
- Payload trees (python/node/go/rust/electron/tauri/saas) — residual to owner
- Inventing answer keys not published in COORD outbox

## Facts file path
- Umbrella: `goals/riso-lanes-assurance/facts.md`
- Lane: `goals/riso-lane-platform/facts.md` + `plan.md` + `OPERATING.md` + `plan.taskgraph.json`
- Plan: `goals/riso-lanes-assurance/plan.md` (W3)
- Graph: `goals/riso-lanes-assurance/plan.taskgraph.json`
- Board: `goals/riso-lanes-assurance/handoffs-board.md`
- Dirty map: `goals/riso-lanes-assurance/inventory-dirty.md`

## Plan tasks this agent owns (IDs)
**Barrier:** W2 join (residuals OK if they don't block answers).

| ID | Work | parallel_group | lock notes |
|----|------|----------------|------------|
| PL-T01 | Diff COORD outbox keys vs all 23 answers | P0 | answers read |
| PL-T02a | Patch answers shard A (samples 1–8) | P1 | exclusive files only |
| PL-T02b | Patch answers shard B (9–16) | P1 | exclusive files only |
| PL-T02c | Patch answers shard C (17–23 + saas-starter variants) | P1 | exclusive files only |
| PL-T03 | Create/update rust sample answers if handoff accepted | P2 | answers dirs only |
| PL-T04 | QUAL/go template test wiring if PLATFORM-owned | P2 | tests/unit or scripts |
| PL-T05 | Full validate loop all answers | P3 | 23/23 or residual log |
| PL-T06 | Full `render_matrix.py` | P4 | renders via script only |
| PL-T07 | `pytest tests/unit/ci/ -q` | P3 | |
| PL-T08 | quality/testing parity review | P3 | quality/** testing/** only if needed |
| PL-T09 | `just quality` | P5 | |
| PL-T10 | Conditional context/agents validators | P5 | if those surfaces changed |

**Answer-file parallel rule:** PL-T02a/b/c only if each sample file exclusive to one shard. Never two agents edit same answers file.

Handoffs owned:
- `graphql-sample-coverage` → PL-T02* (after W1-H06 policy)
- `PLATFORM-rust-samples` → PL-T03
- `PLATFORM-go-api-features-answers` → PL-T02* (monitor)
- `QUAL-go-template-tests` → PL-T04
- Source already filed: `goals/riso-lane-platform/outbox/coord-mcp-languages-typescript.md` (COORD applies)

## COORD outbox paths to read
- **Required before PL-T01:** all of `goals/riso-lane-coord/outbox/*.md` after W1-OUT
- SYS QUAL/rust handoffs under `goals/riso-lane-sys/handoffs/`
- PY graphql sample handoff under `goals/riso-lane-py/handoffs/graphql-sample-coverage.md`

## Dirty paths assigned
From inventory (67 paths — largest PLATFORM dirty set):
- Package: `goals/riso-lane-platform/**` (OPERATING, audit/**, facts*, goal, inbox, outbox, plan*)
- Answers (M): api-monorepo, api-python, changelog-*, circleci-node, docs-docusaurus, docs-fumadocs-full, docs-sphinx, full-stack, gitlab-ci-python, go-api
- Scripts (M): `scripts/ci/render_matrix.py`, `scripts/render-samples.sh`, `scripts/hooks/quality_tool_check.py`, `scripts/hooks/workflow_validator.py`
- Tests: `??` `tests/unit/ci/test_*.py` (5), `M` `tests/unit/test_go_templates.py`

## Verify commands (copy-paste)
```bash
# Per-file validate (all 23)
for f in samples/*/copier-answers.yml; do
  uv run riso validate --answers-file "$f" --json || echo "FAIL $f"
done

uv run python scripts/ci/render_matrix.py
uv run pytest tests/unit/ci/ -q
uv run pytest tests/unit/test_go_templates.py -q
uv run python scripts/ci/check_quality_parity.py || true
just quality
# conditional if context/agents surfaces changed
uv run python scripts/ci/verify_context_sync.py
uv run python scripts/ci/validate_agents_ecosystem.py
uv run python scripts/ci/validate_jinja_templates.py
```

## Handoff template path if blocked
- Residual: `goals/riso-lanes-assurance/residuals/PLATFORM.md`
- Evidence: `goals/riso-lanes-assurance/evidence/` (e.g. W3-render_matrix.log, W3-just-quality.log)
- Missing COORD keys → residual / re-enter W1; never invent keys
- Matrix flake → one retry then residual with log path

## Done =
PL-T01…T10 green or residual ledger complete with evidence paths; full bar (quality + 23 validates + render_matrix) green or owned residuals; board updated.
