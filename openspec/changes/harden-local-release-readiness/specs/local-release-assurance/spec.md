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

### Requirement: Release assets contain the selected package version

Release preparation MUST build and validate fresh package assets after applying
the selected version, and MUST stop before attachment when building fails.

#### Scenario: A new semantic version is selected

- **WHEN** prepare applies the next release version
- **THEN** fresh wheel and source distributions are built from that version before
  the release plugin attaches them
