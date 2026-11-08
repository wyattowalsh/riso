# Feature Specification: JWT Auth + Argon2 Password Hashing

**Feature Branch**: `018-jwt-argon2`\
**Created**: 2026-08-18\
**Status**: Draft\
**Owner**: Platform Team\
**Input**: Wave C — JWT authentication and Argon2 password hashing for the Python API track. Not SaaS Clerk/Auth.js.

## Scope

Optional **Python FastAPI** auth: password sign-in, Argon2 hashes at rest, JWT access tokens (refresh optional in MVP), FastAPI dependencies for protected routes.

This directory is **spec scaffolding only**. No template or runtime implementation in this draft.

## Out of Scope

- SaaS starter Clerk, Auth.js, WorkOS, or Next.js session cookies (`specs/012-saas-starter`)
- Full OAuth2 social providers, MFA/2FA, and RBAC hierarchies from `specs/ideas.md` idea **011**
- Shipping auth without a persistence story — user/hash storage depends on `017-sqlmodel-alembic`
- Hand-editing `samples/*/render/`
- Tagging `v2.0.0`

## User Scenarios & Testing

### User Story 1 - Register and sign in (Priority: P1)

A developer gets register/token routes: passwords are hashed with Argon2; successful sign-in returns a JWT.

**Why this priority**: Core API auth without pulling in the SaaS stack.

**Independent Test**: Register, sign in, call a protected route with `Authorization: Bearer`.

**Acceptance Scenarios**:

1. **Given** Python API + auth enabled, **When** a user registers with a password, **Then** only an Argon2 hash is stored
1. **Given** valid credentials, **When** they request a token, **Then** they receive a signed JWT
1. **Given** a wrong password, **When** they request a token, **Then** the API returns 401 without leaking whether the user exists (uniform error)

______________________________________________________________________

### User Story 2 - Protect routes (Priority: P1)

Developers mark routes as authenticated via a documented FastAPI dependency.

**Why this priority**: Tokens are useless without a standard dependency.

**Independent Test**: Protected route returns 401 without a token and 200 with a valid token.

**Acceptance Scenarios**:

1. **Given** a protected route, **When** called without a Bearer token, **Then** the response is 401
1. **Given** an expired or tampered JWT, **When** called, **Then** the response is 401
1. **Given** a valid JWT, **When** called, **Then** `current_user` is available to the handler

______________________________________________________________________

### User Story 3 - GraphQL Bearer placeholder (Priority: P2)

GraphQL context already has a JWT **EXTENSION POINT**. When 018 ships, that placeholder uses the same validator as FastAPI.

**Why this priority**: One token story across REST and GraphQL; not a second auth stack.

**Independent Test**: GraphQL field with `auth_required` succeeds only with a valid Bearer token after wiring.

**Acceptance Scenarios**:

1. **Given** 018 not yet implemented, **When** GraphQL runs, **Then** Bearer parsing stays a no-op extension point
1. **Given** 018 implemented, **When** GraphQL and REST share the validator, **Then** the same secret and algorithm apply

### Edge Cases

- Empty password, oversize password, and unicode passwords: reject or hash per documented policy
- Algorithm confusion (`alg: none`): reject
- Clock skew: small leeway documented; do not disable `exp`
- SaaS module also enabled: Python API JWT must not be replaced by Clerk/Auth.js

## Requirements

### Functional Requirements

- **FR-001**: Python API auth MUST use JWT for access tokens and Argon2id (or Argon2 documented variant) for password hashes
- **FR-002**: Secrets MUST come from settings/env, never committed defaults used in production
- **FR-003**: Password hashes MUST NOT be logged or returned in API bodies
- **FR-004**: Auth MUST be optional and independent of `saas_infra_module`
- **FR-005**: Protected-route dependency MUST be the documented extension point for REST
- **FR-006**: GraphQL Bearer validation MUST reuse REST JWT validation when both are enabled
- **FR-007**: User persistence MUST follow `017-sqlmodel-alembic` (do not invent a parallel store)
- **FR-008**: This spec MUST NOT implement Clerk, Auth.js, or other SaaS auth providers

### Key Entities

- **Credential**: username/email + password (plaintext only in transit)
- **PasswordHash**: Argon2 encoded string
- **AccessToken**: JWT with `sub`, `exp`, `iat`
- **AuthSettings**: secret, algorithm (asymmetric optional later), token TTL

## Success Criteria

- **SC-001**: Register + token + protected route works in a rendered Python API with auth on
- **SC-002**: Auth off leaves FastAPI baseline routes public as today
- **SC-003**: No Clerk/Auth.js imports appear in the Python API auth module
- **SC-004**: Offline brute-force of a captured hash is Argon2-hard, not reversible

## Dependencies

- **Requires** `017-sqlmodel-alembic` for storing users and hashes
- GraphQL scaffold (`007`) already has the Bearer extension point
- Distinct from `specs/ideas.md` idea **011** and from shipped `specs/010` (API versioning)
