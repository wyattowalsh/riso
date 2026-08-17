# Lane SAAS

## Mission (3 lines)
Finish full SaaS sweep under `template/files/node/saas/**` + `template/files/saas-starter/**` after W1-OUT.
Sequence runtime → hosting/DB → auth → billing, then fan-out integrations/UI/marketing/compliance.
package.json.jinja only SAAS-T01/T02/T10; no new product modules beyond lane plan.

## Exclusive write roots
- `template/files/node/saas/**`
- `template/files/saas-starter/**` (~195 jinja combined)
- `goals/riso-lane-saas/**`

## Forbidden roots
- Non-saas `template/files/node/**` (NODE lane)
- `samples/*/render/**`, lockfile hand-edits, secrets, `riso-mcp`
- COORD / PY / SYS / DESKTOP / CLI / PLATFORM exclusive roots
- Root saas `package.json.jinja` from non-owner shards (see package_json_owners)

## Facts file path
- Umbrella: `goals/riso-lanes-assurance/facts.md`
- Lane: `goals/riso-lane-saas/facts.md` + `goals/riso-lane-saas/plan.md` + `goal.md`
- Plan: `goals/riso-lanes-assurance/plan.md` (SAAS sub-graph)
- Graph: `goals/riso-lanes-assurance/plan.taskgraph.json`
- Board: `goals/riso-lanes-assurance/handoffs-board.md`
- Dirty map: `goals/riso-lanes-assurance/inventory-dirty.md`

## Plan tasks this agent owns (IDs)
**Barrier:** W1-OUT. Longest W2 path — S0 serial → S1–S3 chain → S4 fan-out (≤4 workers) → S5–S6.

| ID | Work | parallel_group | notes |
|----|------|----------------|-------|
| SAAS-T01 | Runtime (Next/Remix) shared roots | S0 | serial first; may edit package.json |
| SAAS-T02 | Hosting/DB/ORM wiring | S1 | may edit package.json |
| SAAS-T03 | Auth layer | S2 | |
| SAAS-T04 | Billing layer | S3 | depends auth |
| SAAS-T05a | Integrations batch A | S4 | parallel integrations |
| SAAS-T05b | Integrations batch B | S4 | |
| SAAS-T05c | Integrations batch C | S4 | |
| SAAS-T06 | UI/components | S4 | careful package.json lock |
| SAAS-T07 | Marketing pages | S4 | |
| SAAS-T08 | Compliance | S4 | |
| SAAS-T09 | Observability/tests | S5 | |
| SAAS-T10 | saas-starter config/README align | S5 | may edit package.json |
| SAAS-T11 | Validate all saas-starter answer variants | S6 | 10+ variants |

**package.json collision rule:** only SAAS-T01/T02/T10 may edit root saas `package.json.jinja` unless shard owns a nested package exclusively. S4 integrations must not touch root package.json.

## COORD outbox paths to read
- `goals/riso-lane-coord/outbox/` for any contract keys affecting saas modules
- No open SAAS-owned handoffs on board at W0; monitor COORD deltas

## Dirty paths assigned
From inventory (8 paths — package only; **no dirty SAAS product tree**):
- `goals/riso-lane-saas/**` (facts*, goal.md, interview*, plan.md)

## Verify commands (copy-paste)
```bash
# After payload work — saas-starter answer variants (PLATFORM owns answers; validate only here)
for f in samples/saas-*/copier-answers.yml samples/*/copier-answers.yml; do
  [ -f "$f" ] || continue
  case "$f" in *saas*|*full-stack*) uv run riso validate --answers-file "$f" --json ;; esac
done
# Prefer explicit list of saas-starter variants from samples/ when present
uv run python scripts/ci/validate_jinja_templates.py
# SAAS combination smoke (if script present)
uv run python scripts/ci/validate_saas_combinations.py || true
```

## Handoff template path if blocked
- Residual: `goals/riso-lanes-assurance/residuals/SAAS.md`
- Evidence: `goals/riso-lanes-assurance/evidence/`
- Contract/answer gaps → COORD or PLATFORM handoff; never silent cross-lane

## Done =
SAAS-T01…T11 green or residualed; package.json ownership respected; evidence under `goals/riso-lanes-assurance/evidence/`.
