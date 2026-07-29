# Residuals — COORD (W1)

## W1-H06 `graphql-sample-coverage`

| Field         | Value                                            |
| ------------- | ------------------------------------------------ |
| **task_id**   | W1-H06                                           |
| **owner**     | PLATFORM                                         |
| **status**    | residualed (no COORD contract change)            |
| **blocking?** | No for W1 join — sample matrix coverage gap only |

### Policy decision

GraphQL is already a valid `api_features` multiselect choice and dual-gated in hooks/`_exclude`. No `copier.yml` / hooks / catalog change is required for coverage.

Only `samples/changelog-full-stack/copier-answers.yml` currently selects `graphql`. Core python-heavy samples (`api-python`, `full-stack`, `cli-docs`, `docs-sphinx`, `changelog-python`) do not.

### Owner action (PLATFORM — W3 / PL-T02\*)

Extend or add a sample answers file so primary matrix smokes exercise Python GraphQL, e.g.:

- enable `graphql` on an existing combo (`full-stack` or `api-python`), **or**
- add `samples/api-python-graphql/copier-answers.yml`

Never hand-edit `samples/*/render/`; regenerate via official scripts after answers land.

### Evidence

| command                                                                                      | result                      |
| -------------------------------------------------------------------------------------------- | --------------------------- |
| `rg -n 'graphql' samples/*/copier-answers.yml`                                               | only `changelog-full-stack` |
| `uv run riso validate --answers-file samples/changelog-full-stack/copier-answers.yml --json` | `ok: true`                  |

Log: `goals/riso-lanes-assurance/evidence/W1-H06-changelog-full-stack.json`

### Blocking reason (human)

Sample **answers** ownership is PLATFORM exclusive (`samples/*/copier-answers.yml`). COORD must not invent or edit sample answers. Residual is intentional ownership handoff, not a contract defect.
