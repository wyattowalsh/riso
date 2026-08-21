# Plan: SQLModel + Alembic Persistence

**Branch**: `017-sqlmodel-alembic` | **Date**: 2026-08-18 | **Spec**: [spec.md](./spec.md)\
**Status**: Draft | **Owner**: Platform Team

## Goal

Add an **optional** SQLModel + Alembic layer to the Python FastAPI track so generated APIs can persist entities and migrate schema. GraphQL `db` stays an extension point until this spec is implemented.

This document does **not** implement template or runtime code.

## Workstreams (when leaving Draft)

1. **Prompt and deps**: additive Copier flag (key TBD); SQLModel, Alembic, async driver extras only when enabled
1. **Runtime**: engine, session dependency, SQLModel base, example model under `template/files/python/`
1. **Migrations**: Alembic env bound to SQLModel metadata; SQLite + PostgreSQL URLs
1. **GraphQL hook**: replace the `get_db_session` extension point in `graphql_api/main.py.jinja` only as the last wiring task
1. **Tests and sample answers**: maintainer tests + regenerate samples via `./scripts/render-samples.sh` (never hand-edit `samples/*/render/`)

## Non-Goals

- No SaaS Clerk/Prisma/Drizzle work
- No JWT/Argon2 implementation (see `018-jwt-argon2`)
- No `copier.yml` / hook edits in this scaffolding change
- No `v2.0.0` tag

## Technical Context

**Language/Version**: Python 3.11+ (uv)\
**Primary Dependencies**: SQLModel, SQLAlchemy 2.x (via SQLModel), Alembic, asyncpg / aiosqlite as extras\
**Storage**: SQLite (dev/test), PostgreSQL (compose/prod-shaped)\
**Testing**: pytest-asyncio, isolated test DB fixtures\
**Target Platform**: Generated Python API packages\
**Project Type**: Copier templates under `template/files/python/`\
**Constraints**: Optional module; GraphQL session wiring is an extension point until ship; typecheck is **ty**, not mypy

## Constitution Check

| Principle               | Assessment                                                              |
| ----------------------- | ----------------------------------------------------------------------- |
| Template quality first  | Generated persistence code must pass ruff/ty/pylint/pytest when enabled |
| Modular composition     | Opt-in; FastAPI baseline unchanged when off                             |
| Test-driven development | Maintainer tests for include/exclude + rendered persistence tests       |
| Documentation parity    | Module guide + in-project README when implemented                       |
| Backwards compatibility | Additive prompt; no reuse of shipped spec numbers 010–016               |

**GATE**: Pass for Draft. Implementation must re-check before prompt changes.

## Project Structure

### Documentation (this feature)

```text
specs/017-sqlmodel-alembic/
├── spec.md
├── plan.md
├── tasks.md
├── research.md
└── checklists/requirements.md
```

### Planned source (implementation later)

```text
template/files/python/src/{{ package_name }}/db/
├── __init__.py.jinja
├── engine.py.jinja
├── session.py.jinja
└── models/base.py.jinja
template/files/python/migrations/          # Alembic versions + env.py
template/files/python/alembic.ini.jinja
template/files/python/tests/db/
```

GraphQL: keep `# EXTENSION POINT: Implement get_db_session` until the 017 implementation PR.

## Complexity Tracking

No constitution violations in this Draft.
