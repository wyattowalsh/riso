# Roadmap Snapshot

This roadmap condenses the priorities tracked in `specs/` (see
`specs/001-build-riso-template/plan.md`) into Sphinx to keep planning and
documentation in one place. Phases align to the template module catalog and CI
expectations.

## Phase 1 – Critical Infrastructure

| # | Feature | Category | Why now |
|---|---------|----------|---------|
| 004 | Security & Vulnerability Management | Infrastructure | Establishes scanning, SAST, and secret detection baselines. |
| 005 | Container & Deployment Patterns | Infrastructure | Production-ready Docker/compose defaults. |
| 006 | Testing Framework Enhancement | Quality | Stronger pytest coverage and quality automation. |
| 007 | Database & Persistence Layer | Core | Enables persistence, migrations, and pooling. |

**Timeline:** 6–9 months • **Impact:** High

## Phase 2 – Core Capabilities

| # | Feature | Category | Dependencies |
|---|---------|----------|--------------|
| 009 | Authentication & Authorization | Security | 007, 006 |
| 010 | Monitoring & Observability | Operations | 005, 007 |
| 011 | Task Queue & Background Jobs | Core | 007, 010 |
| 012 | Event-Driven Architecture | Architecture | 007, 011 |

## Phase 3 – Developer Experience

| # | Feature | Category | Notes |
|---|---------|----------|-------|
| 013 | Development Environment Management | DevEx | Devcontainers, hot reload, IDE automation. |
| 014 | Code Generation & Scaffolding | DevEx | Generator, templates, and merge-aware updates. |
| 015 | Performance Optimization | Performance | Caching, profiling, load testing. |
| 016 | API Documentation Automation | Documentation | OpenAPI/SDK generation flows. |

## Phase 4 – Advanced Features

| # | Feature | Category | Quick Description |
|---|---------|----------|-------------------|
| 017 | Changelog & Release Management | Documentation | Semantic release + changelog automation. |
| 018 | Architecture Decision Records | Documentation | ADR templates and tooling. |
| 019 | Multi-tenancy Support | Architecture | Database/schema/row-level tenancy. |
| 020 | Feature Flags & Configuration | Operations | Gradual rollouts and A/B testing. |
| 021 | Internationalization (i18n) | Feature | Locale support and translation management. |
| 022 | Notifications & Messaging | Feature | Email/SMS/push/webhooks. |
| 023 | Search & Full-Text Search | Feature | Elasticsearch/Meilisearch adapters. |
| 024 | File Storage & Management | Feature | S3/GCS abstraction and processing. |
| 025 | Webhook Management | Integration | Emission and consumption plumbing. |
| 026 | AI/ML Integration Scaffolding | Feature | LLM APIs, vector DBs, and RAG patterns. |

## Phase 5 – Governance & Operations

| # | Feature | Category | Quick Description |
|---|---------|----------|-------------------|
| 027 | Compliance & Audit Logging | Compliance | Immutable trails for SOC2/GDPR/HIPAA. |
| 028 | Data Privacy & GDPR Toolkit | Compliance | Export, deletion, and consent tooling. |
| 029 | Backup & Disaster Recovery | Operations | Automated backups and restore testing. |
| 030 | Cost Optimization & FinOps | Operations | Cost tracking and optimization patterns. |

## Suggested implementation flow

- **Quarter 1–2:** 004 → 005 → 006 (establish security, containers, and quality).
- **Quarter 3–4:** 007 → 009 → 010 (database, auth, observability), then branch
  into 011/012 for asynchronous workloads.
- **Beyond:** Iterate through Phases 3–5 based on adopter demand.
