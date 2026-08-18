# Plan: JWT Auth + Argon2 Password Hashing

**Branch**: `018-jwt-argon2` | **Date**: 2026-08-18 | **Spec**: [spec.md](./spec.md)\
**Status**: Draft | **Owner**: Platform Team

## Goal

Add optional JWT + Argon2 auth to generated **Python FastAPI** apps. This is not the SaaS Clerk/Auth.js path.

This document does **not** implement template or runtime code.

## Workstreams (when leaving Draft)

1. **Prompt**: additive Copier flag (key TBD); default off; gated on Python API
1. **Hashing**: Argon2 via `argon2-cffi` (or equivalent maintained binding)
1. **JWT**: issue/verify access tokens; FastAPI `OAuth2PasswordBearer` (or equivalent) dependency
1. **Persistence**: user model + hash column on top of `017-sqlmodel-alembic`
1. **GraphQL**: fill the Bearer extension point in `graphql_api/context.py.jinja` with the shared validator
1. **Tests**: register, login, 401 paths; never assert raw passwords

## Non-Goals

- No Clerk, Auth.js, NextAuth, or WorkOS in this spec
- No MFA, social OAuth, or full RBAC MVP
- No `copier.yml` / hook / sample-render edits in this scaffolding change
- No `v2.0.0` tag

## Technical Context

**Language/Version**: Python 3.11+\
**Primary Dependencies**: PyJWT (preferred over unmaintained `python-jose` for new code), `argon2-cffi`, FastAPI security utilities\
**Storage**: User + hash via spec 017\
**Testing**: pytest; time-frozen JWT expiry tests\
**Constraints**: Optional; secrets from env; algorithm allow-list; ty not mypy

## Constitution Check

| Principle | Assessment |
| --------- | ---------- |
| Template quality first | Auth code must pass quality suite when enabled |
| Modular composition | Independent of SaaS auth; optional on Python API |
| Test-driven development | Negative 401 tests required |
| Documentation parity | Warn that this is not Clerk/Auth.js |
| Backwards compatibility | Additive; do not reuse spec numbers 010–016 |

**GATE**: Pass for Draft. Implementation blocked on 017 shipping (or a documented thin in-memory exception — default is 017 required).

## Project Structure

### Documentation (this feature)

```text
specs/018-jwt-argon2/
├── spec.md
├── plan.md
├── tasks.md
├── research.md
└── checklists/requirements.md
```

### Planned source (implementation later)

```text
template/files/python/src/{{ package_name }}/api/auth/
├── hashing.py.jinja      # Argon2
├── jwt.py.jinja          # issue/verify
├── deps.py.jinja         # FastAPI dependencies
└── routes.py.jinja       # register / token
```

WebSocket JWT comments in `websocket/decorators.py.jinja` should reuse the same verifier when both modules are on — do not copy a second JWT stack.

## Complexity Tracking

No constitution violations in this Draft. Dual auth (SaaS + Python JWT) is an explicit non-merge: both may exist in one monorepo as separate packages; they must not share cookie/session semantics.
