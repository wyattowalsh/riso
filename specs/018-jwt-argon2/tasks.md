# Tasks: JWT Auth + Argon2 Password Hashing

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [research.md](./research.md)\
**Status**: Draft | **Owner**: Platform Team | **Date**: 2026-08-18

Scaffolding is done. Do **not** implement template/runtime work until this spec leaves Draft. Depends on `017-sqlmodel-alembic` for user storage. Not Clerk/Auth.js.

## Phase 1: Research and design

- [x] R001 [P] Lock Argon2id + JWT; exclude SaaS Clerk/Auth.js
- [x] R002 [P] Prefer PyJWT for new code; migrate WebSocket jose comments later
- [x] R003 [P] Require 017 for user/hash persistence
- [ ] D001 Write token claim and error-body contract
- [ ] D002 Write user model fields against 017 data-model
- [ ] D003 Confirm Copier prompt key — ask before `copier.yml`

## Phase 2: Implementation (blocked on Draft + 017)

- [ ] T001 Add Argon2 hashing helpers under `template/files/python/src/{{ package_name }}/api/auth/`
- [ ] T002 Add JWT issue/verify + FastAPI deps
- [ ] T003 Add register/token routes and user model (017)
- [ ] T004 Wire GraphQL Bearer extension point to the shared verifier
- [ ] T005 [P] Point WebSocket JWT helper at the same verifier when both enabled
- [ ] T006 [P] Module docs: “Python API JWT, not SaaS Clerk/Auth.js”
- [ ] T007 Maintainer include/exclude tests; 401 cases

## Phase 3: Validation

- [ ] V001 Register, token, protected route in a render
- [ ] V002 Expired/tampered/`alg: none` rejected
- [ ] V003 Hashes never appear in logs or JSON fixtures committed to git
- [ ] V004 Sample regeneration via `./scripts/render-samples.sh` only

## Dependencies

- After `017-sqlmodel-alembic`
- Independent of `019-otel-metrics` except optional auth metrics later
- Must not collide with shipped `012` SaaS auth files
