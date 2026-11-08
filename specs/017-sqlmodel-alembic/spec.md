# Feature Specification: SQLModel + Alembic Persistence

**Feature Branch**: `017-sqlmodel-alembic`\
**Created**: 2026-08-18\
**Status**: Draft\
**Owner**: Platform Team\
**Input**: Wave C — SQLModel + Alembic persistence for the Python FastAPI track. GraphQL context session remains an extension point until this spec ships.

## Scope

Optional persistence for generated **Python FastAPI** apps: SQLModel models, async sessions, and Alembic migrations (SQLite for local/test, PostgreSQL for production-shaped renders).

This directory is **spec scaffolding only**. No template, hook, Copier prompt, or sample-render implementation belongs to this draft.

## Out of Scope

- Node, Go, Rust, Prisma, Drizzle, or SaaS-starter databases
- GraphQL `db` session wiring (keep the existing **EXTENSION POINT** until this spec is implemented)
- JWT/auth user tables beyond a documented hook for `018-jwt-argon2`
- Hand-editing `samples/*/render/`

## User Scenarios & Testing

### User Story 1 - Persist API entities (Priority: P1)

A developer renders a Python API and gets a SQLModel session dependency, a base model, and one example entity they can extend.

**Why this priority**: Without a session and model pattern, FastAPI stays in-memory.

**Independent Test**: Render with the persistence option on, start the API, create and read an example row through a documented endpoint or fixture.

**Acceptance Scenarios**:

1. **Given** Python API + persistence enabled, **When** the project is rendered, **Then** SQLModel models, engine/session helpers, and Alembic config are present
1. **Given** that project, **When** tests run, **Then** example persistence tests pass against an isolated database
1. **Given** persistence disabled, **When** the project is rendered, **Then** no SQLModel/Alembic runtime files are added

______________________________________________________________________

### User Story 2 - Migrate schema with Alembic (Priority: P1)

A developer changes models and produces a revision, then upgrades and downgrades without hand-writing SQL for the happy path.

**Why this priority**: Schema history is the production gate for persistence.

**Independent Test**: Autogenerate a revision from a model change, `upgrade head`, then `downgrade -1`.

**Acceptance Scenarios**:

1. **Given** a model change, **When** the developer generates a revision, **Then** Alembic records upgrade and downgrade operations
1. **Given** a fresh render, **When** they apply migrations, **Then** the database reaches head without manual SQL
1. **Given** SQLite (dev/test) or PostgreSQL (compose/prod-shaped), **When** migrations run, **Then** both backends are documented and smoke-tested

______________________________________________________________________

### User Story 3 - Isolate tests from developer databases (Priority: P2)

CI and local pytest use a throwaway database (or file) so developers do not share state with `dev.db`.

**Why this priority**: Flaky shared SQLite files break the quality suite.

**Independent Test**: Two pytest sessions in parallel do not see each other's rows.

**Acceptance Scenarios**:

1. **Given** API tests, **When** they run under `uv run pytest`, **Then** they use a test-scoped engine/session fixture
1. **Given** a failed test, **When** the next test starts, **Then** schema and data start from a known migration head

### Edge Cases

- Persistence enabled without a database URL: fail at startup with a clear settings error
- Concurrent Alembic upgrades: document a single-writer rule; do not auto-repair split brains
- GraphQL enabled before this spec ships: `get_db_session` stays commented as an extension point
- SQLModel chosen over raw SQLAlchemy 2.0 in `specs/ideas.md` bullet 010 — that idea number is **not** this spec

## Requirements

### Functional Requirements

- **FR-001**: Generated Python FastAPI projects MUST be able to opt into SQLModel persistence without enabling SaaS infra
- **FR-002**: The template MUST provide a request-scoped async session dependency for FastAPI routes
- **FR-003**: The template MUST ship Alembic with autogenerate against SQLModel metadata
- **FR-004**: Settings MUST accept a database URL for SQLite and PostgreSQL
- **FR-005**: Tests MUST migrate (or create schema from metadata in unit scope) without touching a developer’s default database file
- **FR-006**: Until this spec is implemented, GraphQL context MUST keep `db` as an extension point (`graphql_api/main.py` `get_db_session` comments)
- **FR-007**: When this spec ships, GraphQL context MAY receive the same session dependency; that wiring is part of 017 implementation, not 007
- **FR-008**: Copier prompts and hooks for this module MUST be additive and off by default (keys decided at implementation; not added in this draft)

### Key Entities

- **DatabaseSettings**: URL, echo, pool options
- **SessionFactory**: async engine + sessionmaker
- **SQLModelBase**: shared metadata for Alembic
- **AlembicRevision**: versioned upgrade/downgrade script
- **ExampleModel**: one documented entity for smoke tests

## Success Criteria

- **SC-001**: Fresh Python API + persistence render applies migrations and passes packaged persistence tests without extra setup beyond documented env vars
- **SC-002**: Disabling the option leaves the FastAPI baseline unchanged
- **SC-003**: GraphQL renders continue to work while `db` is still an extension point
- **SC-004**: Maintainer tests cover render inclusion/exclusion; no sample-render hand edits

## Dependencies

- Requires shipped FastAPI track (`specs/006-fastapi-api-scaffold`)
- Unlocks `specs/018-jwt-argon2` user/password storage
- Distinct from `specs/ideas.md` idea **010** (backlog numbering)
