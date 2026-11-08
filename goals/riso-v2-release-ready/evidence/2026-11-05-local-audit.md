# Local release audit — 2026-11-05

**Status:** the local hardening checkpoint is committed as `c1980b1`. The
authorized merge of both main histories remains in progress, targeting
`93ee6aeb93622315b900aa7995798b905165a0dd`. The automatic file-protection hook
rejects changes to four tracked example environment templates despite explicit
maintainer approval. The full matrix, merge commit, and remote synchronization
remain pending. No release, tag, or deployment has been published.

This audit starts from clean local `main` at `9a5208031cbdd4024563b7f5092090ba94a2a2f6`.
Fetched upstream `main` is `93ee6aeb93622315b900aa7995798b905165a0dd`.
Their initial commits have identical trees but different commit identities; Git
reports no common ancestor. The maintainer explicitly requested preserving and
merging both histories on local main, assuring the combined result, then updating
remote main. No history rewrite or new branch is needed.

## Restored strict quality

Generated Just, Make, and Taskipy use one strict Ruff configuration. It extends
the standard checks with async, timezone, Python correctness, and security rules.
The previous `--select ALL` enabled incompatible rules and picked up new rules
whenever Ruff changed. Strict ty still treats warnings as errors, Pylint still
checks errors, and branch coverage uses the existing generated floor. The sample
renderer now runs the declared profile even if the calling shell selects another
profile. [Ruff rule selection](https://docs.astral.sh/ruff/linter/#rule-selection)

Fresh ordinary Copier outputs passed strict Ruff before renderer normalization.
All three quality runners then passed on the following projections. The
production-source column filters the measured data to `src/` for comparison.
The existing runner coverage includes both source and tests.

| Projection | Tests per runner | Strict branch coverage | Production source |
| --- | ---: | ---: | ---: |
| Full-stack Python | 301 | 95.29% | 92.91% |
| GitLab Python | 151 | 95.47% | 92.54% |
| Standalone GraphQL and WebSocket with MCP examples disabled | 130 | 95.74% | 92.62% |

The generated entry-point tests cover the repaired behavior.

- FastAPI binds to loopback by default, rejects production reload settings, and
  honors an explicit empty CORS list in every environment. Partial updates can
  clear nullable fields and preserve omitted fields.
- WebSocket admission rejects oversized JSON, throttling sends retry metadata,
  and heartbeat timeout removes inactive connections. The endpoint decorator
  supplies the connection ID without requiring a request parameter.
- GraphQL masks system errors on both HTTP entry points and preserves public
  validation information. The generated credential validator rejects all
  credentials until the application supplies its own. Python MCP bounds each
  HTTPX operation within the existing cumulative DNS and HTTP deadline.
- The CLI preserves existing configuration on serialization errors, avoids
  logging raw environment values, and emits parseable structured output.

The direct runner logs are `strict-{full,alternate}-final-runners.log` and
`strict-gitlab-verified-runners.log`. The separate source measurements are
`strict-{full,alternate}-final-production-coverage.log` and
`strict-gitlab-production-coverage.log`.

The official `full-stack`, `changelog-full-stack`, and `gitlab-ci-python`
renders now pass the Just and Taskipy quality smoke stages. Those official
answers render Just only. The direct checks above select both Just and Make.
The full-stack environment resolves to the same 126 public package versions
as the previously audited graph.

All 25 non-SaaS official samples have current passing render receipts and pass
Docker Compose configuration validation. The 12 protected SaaS renders and the
complete matrix snapshot are still pending. The local receipt is
`strict-profile-official-refresh-receipt.json`.

Fresh Python MCP-only projects pass `python -m <package>.mcp --help` and
in-memory MCP sessions with examples enabled or disabled. Their strict Taskipy
checks pass at 96.48% and 92.63%, respectively, against the 85% floor. Tests verify
that the MCP error helpers preserve their public codes and structured payloads
after the package move. An additional 40 maintainer tests pass with the audited
FastMCP and HTTPX versions available.

The selected maintainer suite reports 1,636 passing tests, 22 skips, and
74.08% coverage against the 70% floor. Four tests that read protected templates
were deselected. Its sole failure is the removal check for the legacy frontend
tree, where the three protected examples remain. The web production build,
maintainer lint and type checks, Actionlint, and context/version checks pass.

## Earlier strict and optional API qualification

Before strict quality was restored, the non-SaaS render receipt covered only the
smoke stages that ran. The renderer skipped aggregate commands for strict samples.
Direct runs found 455 Ruff diagnostics in GitLab Python and 1,118 in full-stack
before the optional API corrections. `--select ALL` enables conflicting Ruff
conventions. The GitLab sample still passes 103 tests, strict ty and Pylint's
error checks, but its measured branch coverage is 87.89% against the existing
90% floor. The strict lint policy and coverage floors were kept in place. See
`strict-gitlab-quality.log`, `strict-full-stack-online-quality.log`, and
`strict-gitlab-ci-python-coverage-direct.log` in the local receipts.

The full-stack strict suite exposed real GraphQL startup failures. Its standalone
test package named `graphql` masked the SDK. After fixing that collision, the
subscription lacked an annotation, legacy `PageInfo` annotations could not be
resolved, and both routers used a removed option and an incompatible context.
The current template uses Strawberry 0.340.0 or newer, request-scoped extension
instances, a shared connection context, and the actual GraphQL HTTP entry points.
Anonymous requests can query public fields and cannot use the example mutations.
Cursor pages advance with stable totals, and the depth and cost rules check named
fragments and variable page sizes. The isolated generated suite passed 26 tests
with Strawberry 0.340.0 and graphql-core 3.3.1. It also verified that production
ignores the playground opt-in. Scoped strict ty and Pylint error checks pass.

The pre-change installed Python dependency audit identified unfixed findings in
`python-jose` 3.5.0 and its `ecdsa` 0.19.2 dependency. The existing generated
WebSocket dependency group now declares PyJWT 2.15.1 or newer. The two refreshed
full-stack samples install identical sets of 126 public package versions. The
installed audit reports zero known findings for that graph, excluding the one
editable sample distribution. This graph is separate from the maintainer's
Python audit.

The generated WebSocket routes now invoke admission and message middleware in
registration order. Rejected or cancelled handshakes release capacity, and
cancelled closes remove the connection from the manager. An isolated ASGI run
passed 35 tests, including real HS256 and RS256 signatures, wrong algorithms and
keys, expired tokens, message rejection, and successful routes without middleware.
Both GraphQL entry points also complete the actual `graphql-transport-ws`
handshake, event delivery, and stream completion.

The refreshed `full-stack` and `changelog-full-stack` samples pass their selected
GraphQL, WebSocket, API, CLI, and MCP smoke tests. Direct execution collects 188
passing tests in each. Full-stack strict ty and Pylint's error checks pass.
At that checkpoint, both variants measured 82.79% branch coverage against the
90% floor, and full-stack reported 1,141 findings under the all-rules Ruff
command. Both aggregate strict profiles failed at that checkpoint.

SaaS source changes align the selected workspace, framework output paths, and
startup command. When combined, the Compose services have distinct host ports
for Fastify, Fumadocs, and SaaS. Next.js and Remix isolated compiler fixtures emit
the expected paths, and six synthetic SaaS Compose projections pass the actual
Compose CLI. The SaaS runtime retains its locked install tree because pnpm pruning
removed workspace links or generated Prisma artifacts in focused fixtures.
These are compiler and configuration checks. The protected official samples,
final locks, Docker image startup, and providers still need qualification.

The earlier Compose run caught a null service map in the desktop and TypeScript
MCP samples. The correction emits an empty mapping when
no service is selected. It preserves the other 22 projections byte for byte.
The rerender and CLI results are in `optional-api-refresh-final-receipt.json`.

The latest broad selected maintainer run reports 1,633 passed, 22 skips, one
frontend-removal failure, four protected-reading tests deselected, and 74.08%
coverage against the 70% floor. The later empty-service Compose regression
passed with the other 15 container template checks. The strict docs and web
production build also passed after the API testing guide update.

The Docusaurus OpenAPI advisory was rechecked against the current registry and
Postman development manifest. The Postman SDK still uses Faker 5.5.3. The patched
Faker API cannot initialize the current SDK and lacks 46 of the 110 referenced
methods. The available Scalar integration would change the generated per-operation
routes to a single client route, so the current feature and its open advisory
remain in place.

## Resumed runtime audit

The protected operations remain denied, but the SaaS-disabled tracks can be
rendered normally without resolving or excluding any protected source file.
Additional qualification exposed gaps beyond the earlier checkpoint below:

- Five official Python variants pass CLI/API/docs checks. Standard-profile
  quality checks pass; the strict GitLab sample's official smoke explicitly skips
  its quality runners.
- The default docs project builds, but its generated `next lint` command fails
  under Next.js 16. A fresh generated-workspace audit reports one moderate
  minimatch advisory through the TypeScript ESLint parser. The maintainer/web
  audit results below cover different dependency graphs.
- All six Go/Rust official renders exit zero, yet actual native qualification
  initially produces ten passing and seventeen failing stages. The built-in
  smoke records did not run native compiler or formatter checks.
- Go workspace comments are invalid, an API-disabled CLI emits an empty source
  file, and combined CLI/API server imports cross a Go internal-package boundary.
- Rust's complete generated projects have formatting and integration-test
  defects beyond the earlier isolated API-core proof. The MCP HTTP-fetch tool
  also truncates UTF-8 at an arbitrary byte boundary and can panic.

The native workspace, formatting, and test defects are corrected. The approved
Go default is 1.27 (alternate 1.26); three official Go samples pass workspace,
formatting, tidy, build, test, and vet on the existing Go 1.27.2 with automatic
toolchain downloads disabled. The CLI now rejects explicitly missing or malformed
configuration instead of storing a nil configuration; three generated behavioral
cases pass. The API's `[no test files]` results remain compiler-only proof.

The fresh Go API/CLI graphs exposed advisories in resolved dependencies, so
direct dependencies and applicable transitive selections were refreshed. Gin,
Fiber, Echo, and Chi combined CLI/API fixtures all pass the native gates with
canonical `1.26.0` workspace and module declarations on Go 1.27.2. The official
Go API and CLI samples also pass with `1.27.0` declarations. The Go DB's remaining
OpenPGP advisory on the Gin/Echo crypto module has no matching imported package
in those builds. This is not a standard-library or vulnerable-function scan.

The maintainer approved a separate Rust 1.99.1 installation and three generated
build-toolchain pin updates. The existing stable default was retained. All three
official Rust samples pass formatting, check, tests, and strict Clippy explicitly
on 1.99.1: API 10 tests plus three ignored extension points, CLI seven tests, MCP
15 tests. Cargo's declared 1.89 minimum remains unchanged and untested at that
minimum. Node/Rust MCP HTTP tools now validate all resolved addresses and pin
actual connections, bound the complete operation, and preserve output semantics.
The Go MCP HTTP tool now has the same pinned public-address policy. Official Go
MCP regeneration, native tests, and a built stdio protocol smoke pass; the SDK
was updated to 1.8.0 and the nine compiled dependency modules yield no OSV
matches. The examples-disabled variant emits no blank Go source stubs. The
Python HTTP tool now pins validated addresses with the original HTTP Host and
TLS server identity, disables ambient proxies, and bounds DNS through body read.
Its explicit public HTTP opt-in remains supported. The generated server lives
under the project's own package instead of shadowing the top-level MCP SDK;
noneditable installs and official full-stack samples pass actual stdio startup.
The normal renderer now runs the shipped Python MCP test suite when selected.
The generated suite exercises the module launcher, the example tools and
resources through an MCP session, and the HTTP policy through intercepted DNS
and transport. The Riso CLI and wizard reject the reserved package name `mcp`.

A fresh Rust lock audit then exposed Actix's unused HTTP/2 dependency and the
old Rust MCP SDK. The generated plaintext Rust API no longer enables the
advisory-bearing HTTP/2 stack; all native gates and a 184-crate lock audit pass.
Rust MCP was moved to SDK 3.9. The official stdio sample and generated HTTP/SSE
fixtures pass formatting, compilation, tests, strict Clippy, and actual protocol
round trips on 1.99.1. The SSE selection uses Streamable HTTP and the tested
examples-disabled fixture exposes zero tools. All owned processes stopped. The
five current Rust locks have zero version-level OSV matches across 332 unique
crate versions. No resolved Apple ARM dependency declares a minimum above 1.89;
execution at 1.89 has not been tested.

The generated TypeScript MCP package passes type checking, JavaScript/declaration
builds, 86 runtime tests, Biome, and a zero-advisory full dependency audit on Node
22.23.1 and pnpm 9.15. Actual built-entry stdio, HTTP, and SSE protocol round trips
pass; owned servers were stopped. Its resolved dependencies require Node 22.19;
the root workspace intersects this with semantic-release's range when both are
enabled. Four emitted engine profiles and ten version boundaries match the
actual installed SDK requirements; alternate Node runtimes were not executed.

The default Fumadocs sample passes supported ESLint, type checking, build, and a
zero-advisory audit after the targeted minimatch correction. The full-feature
variant also passes these checks after scoped KaTeX and Scalar Undici updates.
Actual math, Mermaid, CSS, and OpenAPI dependency consumers were checked before
the generated workspace audit reached zero.

Fourteen more non-desktop samples all regenerate successfully. Additional
checks caught invalid Fastify route schema metadata, a shared source boundary
failure, and unresolved extensionless imports in the emitted JavaScript despite
passing HTTP tests. Plain and shared layouts now pass the production-only pnpm
deployment and return 200 from their emitted entries. Docker's generated build
and runtime paths match these entries. Generated Compose serves static Fumadocs
and Docusaurus exports on their declared ports. Container rendering contracts
pass; actual Docker builds and the SaaS runtime paths remain unverified.

Docusaurus now passes render, lint, type checking, and build, including the
shared Fastify artifact. Scoped dependency corrections reduce its workspace
audit from 15 advisories to one high Faker finding in the Docusaurus OpenAPI
Postman dependency. The currently patched Faker release is incompatible with
the Postman SDK. A scoped pnpm policy prevents the generator's unlocked nested
installs and warm cache replay; 70 code snippets remain byte-identical. This
variant is not audit-clean.

Electron and Tauri pass generated type checking, build, lint, and tests; Tauri
also passes native format, check, strict Clippy, two tests, and actionlint for
the generated root workflow. Exact public npm version audits find no matches.
Electron's raw pnpm 9 audit still reports 64 historical rows for a synthetic
`electron@0.1.0` workspace importer, while the lock and install select 45.2.3.
No audit rows were suppressed. The Tauri all-target Rust lock has two upstream
Linux/BSD GTK advisories outside the tested Apple ARM dependency graph. Linux,
hosted CI, desktop GUI launch, packaging, and signing remain unverified.

The earlier selected maintainer run reports **1627 passed, 21 skips, one
frontend-removal failure**, and **74.08%** coverage against the unchanged 70%
floor. Nine skips require Docker or PowerShell. Twelve require HTTPX, which is
absent from the maintainer environment; the actual generated runtime was tested
separately. Four protected-reading tests were explicitly deselected. One earlier
interrupted run used two stale selectors, was discarded, and is not verification.
Ruff, ty, context parity, and the version verifier pass. The unfiltered suite and
full hook gate remain pending the protected file operations.

The current wizard passed 356 unit tests and 19 Chromium tests. The production
build, including strict Sphinx and TypeScript, passed again after the testing
guide update. All 37 official answer files pass CLI validation; that does not
execute the generated projects.

All **25 of 25 SaaS-disabled variants** were regenerated through the official
renderer with no failed smoke modules. The three Python MCP variants were rerun
after the package and coverage corrections. Full Fumadocs passes both `just
quality` and `uv run task quality` at **90.35%** coverage against the unchanged
90% floor. The strict full-stack variants pass the Python MCP suite; their
renderer still skips the strict profile's aggregate quality recipes. The separate
examples-disabled fixture passes five shipped tests. These results are recorded
in `tmp/riso-audit-2026-11-05/non-saas-refresh-receipt.json`.

Twelve SaaS-enabled variants still depend on the protected source cleanup.
The tracked wizard prompt data is refreshed; the partial executions do not
replace the final 37-sample render matrix or count as full matrix acceptance.
Exact initial results are in `tmp/riso-audit-2026-11-05/resumed-native/summary.json`
and `tmp/riso-audit-2026-11-05/resumed-python/summary.json`. The shared guard's
source-level diagnosis is in `tmp/riso-audit-2026-11-05/guard-diagnosis.md`; no
general approval exception was found, and no shared enforcement was changed.

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
- Quality-only CI consolidation writes its own summary. Render reuse rejects
  missing, empty, malformed, duplicate, or inconsistent records before rewriting
  evidence; valid failed records still fail the gate. The focused matrix suite
  passes 65 tests.
- Container publishing builds once, scans its immutable digest, copies that same
  image/index and attestations to GHCR, and verifies every destination digest.
  Twenty-three focused tests and actionlint with ShellCheck on six configurations
  pass. Live registry writes and attestation acceptance remain untested.
- Source archives have bounded installable-asset discovery. Wheels include the
  template and all managed-hook helpers. Four real packaging tests now include
  normal installed copy and changed-answer recopy outside the checkout.
- Required Jinja/YAML libraries are no longer mocked by autosummary. The fresh
  renderer regression, strict HTML build, and strict linkcheck pass. A dead
  research citation is identified as a historical gap; Hacker News uses a truthful
  checker identity rather than Sphinx's rejected legacy browser identity. This
  request-header configuration is mirrored into the generated Sphinx config.
- Test fixture implementation names, delayed imports, docstrings, and subprocess
  defaults were cleaned up without lowering the 9.5 Pylint floor. The final
  combined hook and coverage results are recorded in the local command receipt.

## Earlier merged-source checkpoint

| Check | Observed result |
| --- | --- |
| Official answer validation | 37/37 current answer files pass CLI schema and generation gates |
| Final selected combined pytest coverage | 1534 passed, 9 platform/tool skips, one frontend-removal failure; four protected-reading tests deselected; 74.03% coverage against unchanged 70% floor |
| All-files hooks | All checks pass except the real merge-conflict gate on the protected SaaS example; error checks and the 9.5 Pylint floor remain enabled |
| Installed artifact behavior | Doctor, prompt lookup, validation, normal copy and changed-answer recopy pass outside the checkout, with normal post-generation hooks |
| Distribution metadata | Wheel and source archive pass Twine checks; artifacts remain mechanical smoke evidence while protected source cleanup is pending |
| Wizard | 355 unit tests and 19 Chromium E2E pass; strict docs + TypeScript + Vite production build passes |
| Production browser smoke | Keyboard skip link, 390px without overflow, malformed share rejection, `/docs/` HTTP 200, no page errors |
| Documentation links | Strict check passes: 36 working, four redirects, zero broken |
| SaaS catalogs | All 11 match upstream; three telemetry overwrites restored; nested writer probe preserves catalogs and writes `render-metadata.json` |
| Provider regressions | 52 focused tests pass, including the actual Paddle SDK signature verification contract |
| Rust generated API | Format, check, 10 tests, and strict Clippy pass with existing Rust 1.98; 1.89 floor comes from dependency metadata and is not execution-tested |
| Dependency security | Python OSV, maintainer Node and web audits report zero findings; audited manifests and locks remain unchanged |
| Source mirrors | Context bytes, release-readiness skill mirror, AGENTS ecosystem, and version synchronization pass |

## Remaining enforcement and release gates

The following operations were rejected before execution by the local
`PreToolUse` hook as “Protected secret-bearing file”:

- Resolve `template/files/node/saas/.env.example.jinja` from the reviewed upstream
  example and stage the resolution. This is the only unmerged index path.
- Remove upstream-deleted examples under
  `template/files/frontend/{react/vite,svelte/sveltekit,vue/vite}/.env.example.jinja`.
  These three tracked remnants keep the removed frontend tree present.

No secret contents were printed or written. The hook was not disabled or bypassed.
The maintainer's approval is recorded; repeating an approval question does not
change this enforced denial. The direct environment contract and three broad
SaaS scans remain unchanged and are explicitly excluded from the safe selected
test run. The frontend-removal contract remains enabled and correctly fails.

After those source operations are permitted, required work remains: run the
unfiltered maintainer and hook gates; regenerate all 37 official samples and
matrix snapshots; verify representative generated SaaS builds; rebuild final
artifacts from the clean merged tree; complete the normal merge; push main; and
verify the resulting remote CI. Historical matrix data is not current render
evidence. Docker Desktop's daemon is stopped. Compose configuration can be
checked locally. PowerShell, Rust 1.89 execution, and live registry/provider
acceptance remain unverified.

Production acceptance for Docusaurus OpenAPI remains open on the upstream Faker
advisory. The generated Next.js and Remix SaaS container runtime paths also need
verification with Docker after the protected source operations.

Remote main was checked again during this pass and remains at `93ee6aeb`.
The earlier hardening commit and all pending merge work are preserved on local
main. No new branch, worktree, history rewrite, or forced push was used.

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
a missing hook-helper package path. Rebuilt artifacts and actual copy/recopy now
pass, and that flow is a repository regression test rather than a
doctor-only package check.

Raw command logs and machine-readable reports are local under
`tmp/riso-audit-2026-11-05/`; the live release checklist is
`tmp/riso-prod-ready-release-todo.md`. Final merge, matrix, runtime build, artifact,
hook and synchronization evidence must be appended after those actions complete.
