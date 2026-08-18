# Residuals — COORD (W1)

## W1-H06 `graphql-sample-coverage` — **CLOSED (W3)**

| Field         | Value                                            |
| ------------- | ------------------------------------------------ |
| **task_id**   | W1-H06 / PL-T02                                  |
| **owner**     | PLATFORM                                         |
| **status**    | historical / closed (no COORD contract change)   |
| **blocking?** | No                                               |

### Policy decision (unchanged)

GraphQL is already a valid `api_features` multiselect choice and dual-gated in hooks/`_exclude`. No `copier.yml` / hooks / catalog change was required for coverage.

### Owner action (PLATFORM — W3 / PL-T02) — applied

PLATFORM enabled GraphQL on a primary matrix sample:

- `samples/full-stack/copier-answers.yml` → `api_features: [graphql, websocket]`
- `samples/changelog-full-stack/copier-answers.yml` already had GraphQL (now list form)

Rechecked 2026-08-18. Handoff `graphql-sample-coverage` is **applied** on the board.

Never hand-edit `samples/*/render/`; regenerate via official scripts after answers land.

### Evidence

| source | result |
| ------ | ------ |
| [`ASSURANCE.md`](../ASSURANCE.md) A-T02 | handoff applied; validate_green |
| `evidence/W5-validate-37.json` | 37/37 ok |
| `evidence/W3-PL-T05-validate-summary.json` | 37/37; full-stack + changelog-full-stack ok |
| `evidence/W3-PL-T01-answers-diff.md` | full-stack GraphQL coverage |
| `rg -n 'graphql' samples/*/copier-answers.yml` | `full-stack` and `changelog-full-stack` |
| Historical W1: `evidence/W1-H06-changelog-full-stack.json` | changelog-full-stack already ok |

### Ownership note

Sample **answers** ownership is PLATFORM exclusive (`samples/*/copier-answers.yml`). COORD did not invent or edit sample answers. W1 residual was an ownership handoff, not a contract defect; W3 closed the answers follow-through.

**Active bar residual (not COORD-owned):** PLATFORM R1 full `render_matrix` — [`PLATFORM.md`](./PLATFORM.md).
