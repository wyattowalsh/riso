# Handoffs board — riso-lanes-assurance

Triage of open handoffs for the umbrella assurance goal.\
SSOT mapping: [`plan.md`](./plan.md) § Open handoffs → task mapping · source notes under each lane package.

**Status legend:** `open` (not applied) · `applied` (done) · `monitor` (currently green; recheck if regression) · `partial` (contract vs follow-through split)

**Priority legend:** `P0` blocks sample validate/matrix · `P1` correctness contract · `P2` hygiene / consistency · `P3` optional QUAL expansion

Update this board at each wave join (W1-OUT, W2 join, W3 join, A-T02).

______________________________________________________________________

## Triage table

| id                                 | priority | owner_lane | apply_wave                         | status     | notes                                                                                                                                                                                                                                                                                                                                                                                                   |
| ---------------------------------- | -------- | ---------- | ---------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `coord-mcp-languages-typescript`   | P0       | COORD      | W1 (W1-H01)                        | applied    | Restored `typescript` choice in `mcp_languages`. Outbox: [`goals/riso-lane-coord/outbox/coord-mcp-languages-typescript.md`](../riso-lane-coord/outbox/coord-mcp-languages-typescript.md). Validate mcp-typescript ok:true. NODE follow-through: NODE-T03.                                                                                                                                               |
| `COORD-go-version-mcp`             | P1       | COORD      | W1 (W1-H02)                        | applied    | `go_version` when includes `'go' in mcp_languages`. Outbox: [`goals/riso-lane-coord/outbox/COORD-go-version-mcp.md`](../riso-lane-coord/outbox/COORD-go-version-mcp.md). Validate go-mcp ok:true.                                                                                                                                                                                                       |
| `COORD-rust-module-excludes`       | P2       | COORD      | W1 (W1-H03)                        | applied    | Added `_exclude` for `rust/cli/` and `rust/api/`. Outbox: [`goals/riso-lane-coord/outbox/COORD-rust-module-excludes.md`](../riso-lane-coord/outbox/COORD-rust-module-excludes.md). SYS Cargo member align + PLATFORM rust samples still open.                                                                                                                                                           |
| `exclude-empty-dirs`               | P1       | COORD      | W1 (W1-H04) + PY-T09               | applied    | Codegen `_exclude` + post_gen empty-scaffold cleanup for package-relative optional dirs. Outbox: [`goals/riso-lane-coord/outbox/exclude-empty-dirs.md`](../riso-lane-coord/outbox/exclude-empty-dirs.md). PY-T09 recheck after W1.                                                                                                                                                                      |
| `api-features-normalize`           | P1       | COORD      | W1 (W1-H05)                        | applied    | Hook token-normalize matches CLI; context rewrites `api_features` to sorted list. Outbox: [`goals/riso-lane-coord/outbox/api-features-normalize.md`](../riso-lane-coord/outbox/api-features-normalize.md).                                                                                                                                                                                              |
| `graphql-sample-coverage`          | P2       | PLATFORM   | W1 policy (W1-H06) → W3 (PL-T02\*) | residualed | COORD policy: no contract change; residual → PLATFORM answers. Outbox: [`goals/riso-lane-coord/outbox/graphql-sample-coverage.md`](../riso-lane-coord/outbox/graphql-sample-coverage.md). Residual: [`residuals/COORD.md`](./residuals/COORD.md). PY payload: PY-T03.                                                                                                                                   |
| `PLATFORM-rust-samples`            | P1       | PLATFORM   | W3 (PL-T03)                        | open       | No `samples/rust-{api,cli,mcp}` answers despite modernized `template/files/rust/**`. Author answers only; regenerate via scripts. Source: [`goals/riso-lane-sys/handoffs/PLATFORM-rust-samples.md`](../riso-lane-sys/handoffs/PLATFORM-rust-samples.md). Depends: W1 rust excludes applied if single-module layouts must stay lean.                                                                     |
| `PLATFORM-go-api-features-answers` | P2       | PLATFORM   | W3 (PL-T02\*)                      | monitor    | Historical multiselect shape (`api_features: none` string). SYS recheck: go-api/cli/mcp validate ok:true. Keep answers as lists if regression. Source: [`goals/riso-lane-sys/handoffs/PLATFORM-go-api-features-answers.md`](../riso-lane-sys/handoffs/PLATFORM-go-api-features-answers.md).                                                                                                             |
| `QUAL-go-template-tests`           | P3       | PLATFORM   | W3 (PL-T04) / SYS-JOIN             | open       | `tests/unit/test_go_templates.py` outside SYS write root; currently passes (42). Optional: assert API-only has no `cli/internal`; existence of shared `go/internal/{config,logger}`; bump when MCP default → 1.24. Source: [`goals/riso-lane-sys/handoffs/QUAL-go-template-tests.md`](../riso-lane-sys/handoffs/QUAL-go-template-tests.md). Verify: `uv run pytest tests/unit/test_go_templates.py -q`. |
| `bootstrap-verify`                 | P3       | COORD      | W1-OUT (smoke)                     | applied    | COORD package bootstrap already green (context sync, default validate, prompts, catalog, pytest). Re-smoke at W1-OUT after contract applies; not a new product change. Source: [`goals/riso-lane-coord/outbox/bootstrap-verify.md`](../riso-lane-coord/outbox/bootstrap-verify.md).                                                                                                                     |

______________________________________________________________________

## Counts (after W1 join)

| status                    | count | ids                                                                                                 |
| ------------------------- | ----: | --------------------------------------------------------------------------------------------------- |
| open                      |     2 | rust-samples, QUAL-go-tests                                                                         |
| residualed                |     1 | graphql-sample-coverage (PLATFORM)                                                                  |
| monitor                   |     1 | go-api-features-answers                                                                             |
| applied                   |     6 | bootstrap-verify, mcp-typescript, go-version-mcp, rust-excludes, empty-dirs, api-features-normalize |
| **Apply ownership split** |       |                                                                                                     |

| Wave      | Owner           | Handoffs                                                                                                                          |
| --------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| W1 serial | COORD           | mcp-typescript → go-version-mcp → rust-excludes → empty-dirs → api-features-normalize → graphql policy → catalog/context → outbox |
| W2        | PY / NODE / SYS | empty-dir recheck (PY-T09); TS MCP payload (NODE-T03); GraphQL dual-gate (PY-T03); SYS-H board update                             |
| W3        | PLATFORM        | graphql sample answers; rust sample answers; go-api-features recheck; QUAL go tests; full validate + matrix                       |

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
