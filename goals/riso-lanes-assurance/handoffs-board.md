# Handoffs board — riso-lanes-assurance

Triage of open handoffs for the umbrella assurance goal.\
SSOT mapping: [`plan.md`](./plan.md) § Open handoffs → task mapping · source notes under each lane package.

**Status legend:** `open` (not applied) · `applied` (done) · `monitor` (currently green; recheck if regression) · `partial` (contract vs follow-through split) · `residualed` (owned residual with evidence)

**Priority legend:** `P0` blocks sample validate/matrix · `P1` correctness contract · `P2` hygiene / consistency · `P3` optional QUAL expansion

Update this board at each wave join (W1-OUT, W2 join, W3 join, **A-T02**).

**W4 A-T02 closeout:** **open unowned = 0**. All 10 handoffs applied. Bar residuals (matrix/quality) live in [`residuals/PLATFORM.md`](./residuals/PLATFORM.md), not as open handoffs.

______________________________________________________________________

## Triage table

| id                                 | priority | owner_lane | apply_wave                | status  | notes                                                                                                                                                                                                                                                                                                 |
| ---------------------------------- | -------- | ---------- | ------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `coord-mcp-languages-typescript`   | P0       | COORD      | W1 (W1-H01)               | applied | Restored `typescript` choice in `mcp_languages`. Outbox: [`goals/riso-lane-coord/outbox/coord-mcp-languages-typescript.md`](../riso-lane-coord/outbox/coord-mcp-languages-typescript.md). Validate mcp-typescript ok:true. NODE follow-through: NODE-T03.                                             |
| `COORD-go-version-mcp`             | P1       | COORD      | W1 (W1-H02)               | applied | `go_version` when includes `'go' in mcp_languages`. Outbox: [`goals/riso-lane-coord/outbox/COORD-go-version-mcp.md`](../riso-lane-coord/outbox/COORD-go-version-mcp.md). Validate go-mcp ok:true.                                                                                                     |
| `COORD-rust-module-excludes`       | P2       | COORD      | W1 (W1-H03)               | applied | Added `_exclude` for `rust/cli/` and `rust/api/`. Outbox: [`goals/riso-lane-coord/outbox/COORD-rust-module-excludes.md`](../riso-lane-coord/outbox/COORD-rust-module-excludes.md). PLATFORM rust samples applied W3.                                                                                  |
| `exclude-empty-dirs`               | P1       | COORD      | W1 (W1-H04) + PY-T09      | applied | Codegen `_exclude` + post_gen empty-scaffold cleanup. Outbox: [`goals/riso-lane-coord/outbox/exclude-empty-dirs.md`](../riso-lane-coord/outbox/exclude-empty-dirs.md). PY-T09 recheck green.                                                                                                          |
| `api-features-normalize`           | P1       | COORD      | W1 (W1-H05) + W3 PL-T02\* | applied | Hook token-normalize matches CLI. Outbox: [`goals/riso-lane-coord/outbox/api-features-normalize.md`](../riso-lane-coord/outbox/api-features-normalize.md). Sample answers list-normalized W3 (`0327b1b`); 37/37 validate.                                                                             |
| `graphql-sample-coverage`          | P2       | PLATFORM   | W1 policy → W3 (PL-T02\*) | applied | COORD: no contract change. PLATFORM: `samples/full-stack` now has `api_features: [graphql, websocket]` (+ changelog-full-stack). Evidence: `W3-PL-T01-answers-diff.md`, spot validate full-stack ok:true. Prior residual [`residuals/COORD.md`](./residuals/COORD.md) superseded for coverage action. |
| `PLATFORM-rust-samples`            | P1       | PLATFORM   | W3 (PL-T03)               | applied | Created `samples/rust-{api,cli,mcp}/copier-answers.yml`; validate ok:true (W3-PL-T05). Source: [`goals/riso-lane-sys/handoffs/PLATFORM-rust-samples.md`](../riso-lane-sys/handoffs/PLATFORM-rust-samples.md).                                                                                         |
| `PLATFORM-go-api-features-answers` | P2       | PLATFORM   | W3 (PL-T02\*)             | applied | `go-api` `api_features: []` list form; validate ok:true. Source: [`goals/riso-lane-sys/handoffs/PLATFORM-go-api-features-answers.md`](../riso-lane-sys/handoffs/PLATFORM-go-api-features-answers.md).                                                                                                 |
| `QUAL-go-template-tests`           | P3       | PLATFORM   | W3 (PL-T04)               | applied | QUAL shared-internal asserts landed; `tests/unit/test_go_templates.py` green (W3-PL-T04). Source: [`goals/riso-lane-sys/handoffs/QUAL-go-template-tests.md`](../riso-lane-sys/handoffs/QUAL-go-template-tests.md).                                                                                    |
| `bootstrap-verify`                 | P3       | COORD      | W1-OUT (smoke)            | applied | COORD package bootstrap green. Source: [`goals/riso-lane-coord/outbox/bootstrap-verify.md`](../riso-lane-coord/outbox/bootstrap-verify.md).                                                                                                                                                           |

______________________________________________________________________

## Counts (after W4 A-T02)

| status     | count | ids                                                                  |
| ---------- | ----: | -------------------------------------------------------------------- |
| open       |     0 | —                                                                    |
| residualed |     0 | (handoffs closed; bar residuals are PLATFORM R1/R2 not handoff rows) |
| monitor    |     0 | —                                                                    |
| applied    |    10 | all handoff ids above                                                |

### Non-handoff bar residuals (W3/W4)

| id                          | owner    | status     | residual                                                                                       |
| --------------------------- | -------- | ---------- | ---------------------------------------------------------------------------------------------- |
| PL-T06 full `render_matrix` | PLATFORM | residualed (re-run) | [`residuals/PLATFORM.md`](./residuals/PLATFORM.md) R1 · `evidence/W3-PL-T06-render_matrix-rerun.log` |
| PL-T09 `just quality`       | PLATFORM | **closed green**    | [`residuals/PLATFORM.md`](./residuals/PLATFORM.md) R2 · `evidence/W3-PL-T09-just-quality-rerun.log` (877 pass) |

______________________________________________________________________

## Apply ownership split

| Wave      | Owner           | Handoffs                                                                                                                          |
| --------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| W1 serial | COORD           | mcp-typescript → go-version-mcp → rust-excludes → empty-dirs → api-features-normalize → graphql policy → catalog/context → outbox |
| W2        | PY / NODE / SYS | empty-dir recheck (PY-T09); TS MCP payload (NODE-T03); GraphQL dual-gate (PY-T03); SYS-H board update                             |
| W3        | PLATFORM        | graphql sample answers; rust sample answers; go-api-features; QUAL go tests; full validate + matrix                               |
| W4        | ASSURANCE       | board close + ASSURANCE.md (no product writes)                                                                                    |

______________________________________________________________________

## Plan task crosswalk

| Handoff id                         | Task IDs          |
| ---------------------------------- | ----------------- |
| `coord-mcp-languages-typescript`   | W1-H01            |
| `COORD-go-version-mcp`             | W1-H02            |
| `COORD-rust-module-excludes`       | W1-H03            |
| `exclude-empty-dirs`               | W1-H04 + PY-T09   |
| `api-features-normalize`           | W1-H05            |
| `graphql-sample-coverage`          | W1-H06 / PL-T02\* |
| `PLATFORM-rust-samples`            | PL-T03            |
| `PLATFORM-go-api-features-answers` | PL-T02\*          |
| `QUAL-go-template-tests`           | PL-T04 / SYS-JOIN |
| `bootstrap-verify`                 | W1-OUT smoke      |

______________________________________________________________________

## Residual policy

If a handoff cannot land:

1. Write `goals/riso-lanes-assurance/residuals/<OWNER_LANE>.md` with owner, failing command, redacted log, blocking reason.
1. Put evidence under `goals/riso-lanes-assurance/evidence/`.
1. Set this board `status` to `residualed` (or leave `open` with residual path in notes).
1. Never silent cross-lane edit; never hand-edit `samples/*/render/`.
