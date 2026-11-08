## ADDED Requirements

### Requirement: Sample regeneration stays inside its variant

Automation MUST validate canonical destination containment and matching sample
answers before removing or writing a rendered destination.

#### Scenario: Traversal and symlink escape are rejected

- **WHEN** a variant contains a traversal component or resolves outside samples
- **THEN** regeneration fails before any destination deletion or write

#### Scenario: Nested official variants remain supported

- **WHEN** a nested sample has matching answers under its canonical directory
- **THEN** regeneration accepts its render destination within samples

### Requirement: Tenant and admin operations preserve authorization boundaries

Generated SaaS server code MUST isolate tenant context across asynchronous
requests, fail closed for strict protected operations without a tenant, and check
admin authorization before retrieving administrative data.

#### Scenario: Concurrent tenant requests interleave

- **WHEN** two requests await concurrently in different tenant scopes
- **THEN** each observes only its own tenant and no tenant leaks after completion

#### Scenario: Non-admin requests admin data

- **WHEN** an authenticated non-admin opens an administrative page
- **THEN** access is rejected before administrative queries execute

#### Scenario: Tenant-scoped raw SQL is prepared

- **WHEN** a server prepares a tenant-scoped SELECT query
- **THEN** the helper returns SQL and bound parameters rather than interpolating
  tenant identifiers or appending a filter that an OR expression can bypass

### Requirement: Wizard interchange is validated and lossless

The wizard MUST preserve supported public prompt values through import/export,
validate external shapes and choices, and replace external configuration over
defaults without inheriting unrelated recipient selections.

#### Scenario: Current desktop and SaaS answers round-trip

- **WHEN** valid current public options are imported and exported
- **THEN** their values are retained in the exported Copier answers

#### Scenario: Malformed shared data is rejected

- **WHEN** a shared payload has invalid current-key values
- **THEN** it is rejected before persisted configuration changes

### Requirement: CLI previews and failures preserve destination answers

CLI operations MUST validate explicit selections before normalization and MUST
leave destination answer bytes unchanged when previewing or failing.

#### Scenario: Update worker fails after answer remapping

- **WHEN** canonical answer preparation succeeds but template execution fails
- **THEN** the existing destination answers remain unchanged

### Requirement: Release evidence identifies what was verified

Release evidence MUST distinguish source tests, fresh renders, runtime smoke
checks, installed artifact checks, and unresolved external or permission gates.

#### Scenario: Historical matrix evidence is present

- **WHEN** a snapshot predates the audited source
- **THEN** it is identified as historical rather than current readiness proof

#### Scenario: CI consolidates quality artifacts without a render matrix

- **WHEN** the quality-only consolidation mode receives completed profile artifacts
- **THEN** it writes a separate quality summary without manufacturing or modifying
  render results, and missing input artifacts cause failure

#### Scenario: Reused render evidence is empty or malformed

- **WHEN** render reuse receives empty, malformed, or internally inconsistent
  variant records
- **THEN** it fails before rewriting evidence and never starts fallback renders

### Requirement: Release assets contain the selected package version

Release preparation MUST build and validate fresh package assets after applying
the selected version, and MUST stop before attachment when building fails.

#### Scenario: A new semantic version is selected

- **WHEN** prepare applies the next release version
- **THEN** fresh wheel and source distributions are built from that version before
  the release plugin attaches them

### Requirement: Installed artifacts contain generation assets

Source distributions MUST contain the code, template, and hook helpers needed to
build an operational wheel. Build discovery MUST remain bounded to those assets.

#### Scenario: A wheel runs outside the maintainer checkout

- **WHEN** an installed wheel performs normal copy and recopy operations
- **THEN** the bundled template and managed post-generation helpers resolve
  without importing files from the maintainer checkout

### Requirement: Container promotion preserves the scanned artifact

Generated publishing workflows MUST scan an immutable build digest, stop
promotion on scan failure, and publish that same image/index with its attestations.

#### Scenario: A scanned build is promoted

- **WHEN** the vulnerability scan succeeds
- **THEN** the workflow copies the scanned digest to all intended registry tags
  without rebuilding, and verifies each destination digest

#### Scenario: A scan or digest check fails

- **WHEN** scanning fails or a destination digest differs from the scanned build
- **THEN** the workflow fails and its summary reports the actual result

### Requirement: Native generated tracks are operational

Enabled Go and Rust projects MUST emit valid workspace and source files, obey
language module boundaries, match their shipped formatter settings, and have
integration tests that exercise the actual generated CLI contract.

#### Scenario: Go CLI is generated without a Go API

- **WHEN** the standalone Go CLI is rendered
- **THEN** API-only command files are omitted and its workspace builds without
  disabling workspace processing

#### Scenario: Go CLI serves a generated Go API

- **WHEN** both Go CLI and API tracks are selected
- **THEN** the CLI reaches the API through an allowed public package boundary

#### Scenario: A rendered native track is qualified

- **WHEN** an official Go or Rust sample finishes rendering
- **THEN** native formatting, build, test, and vet or Clippy results are recorded
  separately from smoke modules that did not execute those checks

#### Scenario: An MCP response exceeds its byte limit inside a Unicode character

- **WHEN** the HTTP-fetch tool truncates a valid multibyte response
- **THEN** it retains a valid UTF-8 prefix within the existing byte limit without
  panicking, preserves the original reported content length, and adds no suffix

### Requirement: Generated documentation has current tooling

Next.js documentation projects MUST use a supported lint command and configuration.
Confirmed dependency advisories MUST be corrected without broad overrides of
unrelated dependency consumers.

#### Scenario: Next.js 16 documentation is generated

- **WHEN** its lint, typecheck, and build scripts run
- **THEN** they execute the current supported tools and pass against the generated
  source rather than invoking a removed framework subcommand

### Requirement: Selected runtime versions match the resolved dependency graph

Generated Node engine ranges MUST satisfy the enabled runtime and release
dependencies. Selected Go defaults MUST use a supported release branch. Rust
build-toolchain pins MUST remain distinct from Cargo's declared minimum.

#### Scenario: TypeScript MCP and release automation are both enabled

- **WHEN** the root workspace is generated with both features
- **THEN** its Node engine is the intersection of their dependency requirements
  and qualification records the actual Node and package-manager versions used

#### Scenario: An explicit Go CLI configuration is invalid

- **WHEN** a caller selects a missing or malformed configuration file
- **THEN** command initialization returns the configuration error before storing
  a configuration in the command context or running the command

### Requirement: MCP public HTTP tools enforce their network policy

Generated HTTP tools MUST default to HTTPS, validate canonical destinations, and
connect only to validated public addresses. They MUST preserve their output
semantics and keep the user timeout in force while reading the response. Where
an existing explicit opt-in permits HTTP, the same connection policy MUST apply.

#### Scenario: A destination is private or changes during DNS resolution

- **WHEN** a URL identifies a private address or DNS returns an unsafe address
- **THEN** the request fails before connecting, including alternate numeric or
  mapped-address representations, and a second unchecked lookup cannot bypass
  the validation

#### Scenario: A response body stalls after headers arrive

- **WHEN** a body does not complete within the request deadline
- **THEN** the operation times out and releases its request resources rather
  than dropping the timeout after receiving headers

### Requirement: Generated Python MCP uses the installed SDK

The generated Python MCP server MUST live under the project's Python package.
The CLI and wizard MUST reject a project package name that shadows the SDK.

#### Scenario: A generated MCP project is installed

- **WHEN** a Python MCP project is installed and its server is launched outside
  the generated source tree
- **THEN** its project module imports the separate MCP SDK and starts a session
  with the tools selected by its answers

### Requirement: Selected Python API features run through the generated routes

GraphQL and WebSocket selections MUST run their shipped runtime tests as part of
the sample's Python API smoke with their declared dependency groups.

#### Scenario: GraphQL requests reach the selected router

- **WHEN** the integrated or standalone GraphQL endpoint receives a request
- **THEN** public queries execute, mutations require trusted authentication, and
  validation checks the effective depth and cost of named fragments and list
  selections before resolver execution

#### Scenario: A WebSocket middleware rejects a connection

- **WHEN** a selected WebSocket route invokes registered admission middleware
- **THEN** middleware runs in registration order and rejection leaves no accepted
  connection or reserved capacity

### Requirement: Generated strict Python quality exercises the shipped project

The strict profile MUST keep the standard Ruff rules and extend them with the
generated async, timezone, correctness, and security policy. It MUST run ty with
warnings as errors, Pylint error checks, and branch coverage at the existing floor.

#### Scenario: A maintainer runs a generated strict entry point

- **WHEN** Just, Make, or Taskipy runs strict quality for a rendered Python project
- **THEN** it uses the same strict Ruff configuration, checks the generated
  package and tests, and fails if branch coverage misses the declared floor

#### Scenario: The official renderer builds a strict Python sample

- **WHEN** the sample declares strict quality
- **THEN** the renderer uses that profile for its quality commands even when
  the parent process selects standard quality, and reports failures as failures
