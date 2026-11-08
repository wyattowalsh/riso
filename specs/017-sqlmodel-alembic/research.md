# Research: SQLModel + Alembic Persistence

**Status**: Draft | **Owner**: Platform Team | **Date**: 2026-08-18

## Scope

Choose the persistence stack for the **Python FastAPI** track only. Numbering: this is spec directory **017**, not `specs/ideas.md` idea bullet **010**.

## Decisions

### ORM: SQLModel (not raw SQLAlchemy 2.0 as the public API)

- **Decision**: SQLModel models are the developer-facing layer; SQLAlchemy 2.x remains the engine/session substrate.
- **Rejected**: SQLAlchemy-only models (duplicates Pydantic), Django ORM, Tortoise.
- **Reason**: One model type for API schemas and tables; matches FastAPI/Pydantic v2 already in `006`.

### Migrations: Alembic autogenerate

- **Decision**: Alembic env imports SQLModel metadata; autogenerate is the default path; hand-written ops allowed for data migrations.
- **Rejected**: raw SQL-only folders, Prisma (wrong track).
- **Reason**: Alembic is the Python standard; `fastapi-patterns.md` already documents it as an extension.

### GraphQL session

- **Decision**: Until 017 ships, GraphQL `db` / `get_db_session` stays an **EXTENSION POINT**.
- **Rejected**: Partial GraphQL session stubs in this Draft.
- **Reason**: Avoid half-wired context; `007` already documents the hook.

### Databases

- **Decision**: SQLite for local/test; PostgreSQL URL documented for compose.
- **Rejected**: MySQL as a first-class render target in MVP.
- **Reason**: Matches container module and keeps CI light.

## External references

- SQLModel: <https://sqlmodel.tiangolo.com/>
- Alembic: <https://alembic.sqlalchemy.org/>
- SQLAlchemy asyncio: <https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html>
