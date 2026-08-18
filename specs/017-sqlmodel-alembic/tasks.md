# Tasks: SQLModel + Alembic Persistence

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [research.md](./research.md)\
**Status**: Draft | **Owner**: Platform Team | **Date**: 2026-08-18

Scaffolding is done. Do **not** implement template/runtime work until this spec leaves Draft. Do not edit `copier.yml`, hooks, or `samples/*/render/` in the scaffolding change.

## Phase 1: Research and design

- [x] R001 [P] Record SQLModel + Alembic vs ideas.md 010 numbering split
- [x] R002 [P] Lock GraphQL session as extension point until ship
- [x] R003 [P] Lock SQLite + PostgreSQL URL support
- [ ] D001 Write data-model.md (settings, session, example entity)
- [ ] D002 Write Alembic env/revision contract
- [ ] D003 Confirm Copier prompt key (additive, default off) — ask maintainers before editing `copier.yml`

## Phase 2: Implementation (blocked on leaving Draft)

- [ ] T001 Add optional persistence templates under `template/files/python/src/{{ package_name }}/db/`
- [ ] T002 Add Alembic `env.py` + `alembic.ini.jinja` bound to SQLModel metadata
- [ ] T003 Add FastAPI session dependency and example route or fixture
- [ ] T004 Add pytest DB fixtures under `template/files/python/tests/db/`
- [ ] T005 [P] Document module usage in `template/files/docs/modules/`
- [ ] T006 Wire GraphQL `get_db_session` (replace extension point) only after T001–T003
- [ ] T007 Maintainer tests for include/exclude renders

## Phase 3: Validation

- [ ] V001 Render Python API with persistence on and off
- [ ] V002 `alembic upgrade head` / `downgrade -1` on SQLite
- [ ] V003 `just quality` in the rendered package
- [ ] V004 Regenerate samples via `./scripts/render-samples.sh` only

## Dependencies

- After shipped `006` FastAPI track
- Before `018-jwt-argon2` user storage
- Parallel with `019-otel-metrics` (no shared files if session module stays under `db/`)
