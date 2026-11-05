# Local release audit — 2026-11-05

This audit starts from clean local `main` at `9a5208031cbdd4024563b7f5092090ba94a2a2f6`.
Fetched upstream `main` is `93ee6aeb93622315b900aa7995798b905165a0dd`.
Their initial commits have identical trees but different commit identities; Git
reports no common ancestor. The maintainer explicitly requested preserving and
merging both histories on local main, assuring the combined result, then updating
remote main. No history rewrite or new branch is needed.

## Reviewed source corrections

- Sample regeneration validates canonical variant, answers and destination paths
  before deletion; traversal, mismatched answers and escaping symlinks fail closed.
  Generated mise trust is scoped to the render process instead of persisted.
- External templates cannot choose a Riso-managed hook. Bundled hooks execute in a
  child process with timeout cleanup for descendants, without changing parent cwd,
  environment or argv. Installed wheels include the payload and required helpers.
- CLI generation validates explicit empty selections. Update/recopy defer Riso's
  answer-remap persistence until success and use the source recorded in the
  destination answers; conflicting source overrides fail before generation.
- Tenant context uses asynchronous request scopes, strict Prisma checks fail
  closed, and raw SQL preparation returns bound parameters. Model exclusions use
  Prisma names. Generic tenancy still requires application schema configuration
  and database authorization; unsupported Drizzle operations fail explicitly.
- Global admin data requires a trusted platform role. Server data access and
  client interactions have separate modules. Auth-disabled imports and localized
  sign-in routes are covered by focused runtime tests.
- Wizard interchange validates current public prompt types/choices, preserves
  imported public answers and replaces shared selections over defaults. Integrated
  web builds require and include a strict Sphinx build.
- Release pushes rehearse; publishing requires explicit dispatch. Final assets
  rebuild after applying the selected version. Matrix automation transports and
  stages the tracked web snapshot rather than ignored execution evidence.

## Evidence before history reconciliation

| Check                             | Result                                                                                                      |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Initial maintainer quality        | 1154 passed, 9 platform/tool skips                                                                          |
| First post-fix maintainer quality | 1210 passed, 9 platform/tool skips                                                                          |
| Web unit tests                    | 333 passed                                                                                                  |
| Existing Chromium E2E             | 19 passed                                                                                                   |
| Production browser smoke          | Desktop keyboard skip link, 390px no overflow, malformed share rejection, `/docs/` HTTP 200, no page errors |
| Strict docs + TypeScript + Vite   | Passed                                                                                                      |
| Official answers validation       | 37/37 passed                                                                                                |
| Jinja validation                  | 813 templates passed before final residual edits                                                            |
| Python OSV audit                  | 64 known findings in 10 packages → zero                                                                     |
| Web npm audit                     | 95 advisory entries → zero                                                                                  |
| Root npm audit                    | 57 advisory entries → zero                                                                                  |
| Current diff secret scan          | Zero findings; only redacted classifications retained                                                       |

The pre-merge full sample run was intentionally interrupted after the maintainer
requested history reconciliation. It is not final matrix evidence. It exposed a
generated CLI deprecation failure, corrected to `inspect.iscoroutinefunction`.
The complete official matrix must run again against the reconciled tree.

The first wheel passed metadata/doctor/prompts/validation but normal copy exposed
a missing hook-helper package path. The helper correction requires a rebuilt
wheel and actual copy/recopy smoke outside the checkout; doctor alone is not an
installed-operation gate.

Raw command logs and machine-readable reports are local under
`tmp/riso-audit-2026-11-05/`; the live release checklist is
`tmp/riso-prod-ready-release-todo.md`. Final merge, matrix, runtime build, artifact,
hook and synchronization evidence must be appended after those actions complete.
