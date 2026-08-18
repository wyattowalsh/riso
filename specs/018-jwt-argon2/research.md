# Research: JWT Auth + Argon2 Password Hashing

**Status**: Draft | **Owner**: Platform Team | **Date**: 2026-08-18

## Scope

Python API auth only. Numbering: spec directory **018**, not `specs/ideas.md` idea **011**, and not shipped `specs/010` (API versioning) or `specs/012` (SaaS).

## Decisions

### Password hashing: Argon2 (not bcrypt as primary)

- **Decision**: Argon2id via `argon2-cffi` (parameters documented; OWASP-aligned defaults).
- **Rejected**: bcrypt as the only hasher; passlib as a required facade (optional later).
- **Reason**: Memory-hard hashing; matches the Wave C lock.

### Tokens: JWT access tokens

- **Decision**: Signed JWT access tokens; HS256 acceptable for single-service MVP; RS256 documented as a later option.
- **Rejected**: server-only opaque sessions as the Python API default; Clerk/Auth.js.
- **Reason**: FastAPI APIs typically use Bearer JWTs; SaaS already covers cookie/session providers.

### Library: PyJWT for new code

- **Decision**: Prefer PyJWT for issue/verify in new auth templates.
- **Rejected**: New `python-jose` usage (existing WebSocket comments may be migrated when 018 ships).
- **Reason**: Maintenance and algorithm-confusion hardening.

### Ordering vs 017

- **Decision**: User rows and hashes live in SQLModel models from 017.
- **Rejected**: JSON-file user stores in the shipped template.
- **Reason**: Auth without persistence is a demo-only trap.

### GraphQL / WebSocket

- **Decision**: Reuse one verifier; keep extension points until 018 implementation.
- **Rejected**: Separate JWT secrets per protocol in MVP.

## External references

- Argon2 / OWASP: <https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html>
- PyJWT: <https://pyjwt.readthedocs.io/>
- FastAPI security: <https://fastapi.tiangolo.com/tutorial/security/>
- Argon2id IETF: <https://www.rfc-editor.org/rfc/rfc9106>
