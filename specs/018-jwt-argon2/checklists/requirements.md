# Specification Quality Checklist: JWT Auth + Argon2

**Purpose**: Validate this Draft before implementation\
**Created**: 2026-08-18\
**Owner**: Platform Team\
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation shipped in this change
- [x] Explicitly not SaaS Clerk/Auth.js
- [x] Distinct from ideas.md 011 and shipped specs/010 (versioning)
- [x] GraphQL/WebSocket reuse called out

## Requirement Completeness

- [x] Password hashing algorithm locked (Argon2)
- [x] Token type locked (JWT)
- [x] 401 paths specified
- [x] 017 dependency stated
- [ ] Token claim contract written (D001)
- [ ] Copier prompt key named (ask before `copier.yml`)

## Feature Readiness

- [ ] 017 persistence available or explicitly waived
- [ ] Secret-handling review before implementation PR
- [x] No `v2.0.0` tag in this spec

## Notes

Draft is ready for design follow-up, not for template edits.
