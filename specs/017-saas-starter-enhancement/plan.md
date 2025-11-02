# Implementation Plan: SaaS Starter Comprehensive Enhancement

**Branch**: `017-saas-starter-enhancement` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/workspaces/riso/specs/017-saas-starter-enhancement/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Comprehensive enhancement to the existing 012-saas-starter module that transforms it into an enterprise-grade SaaS application generator. Key improvements include: (1) Expanding technology options from 2 to 4 choices per original category (56 → 80+ total integrations), (2) Adding 7 new infrastructure categories (search, cache, feature flags, CMS, usage metering, secrets management, enhanced error tracking), (3) Visual configuration builder with real-time compatibility validation, cost estimation, and architecture diagram generation, (4) Migration tools enabling post-generation technology swaps with automated code analysis and rollback capability, (5) Multi-tenant B2B SaaS patterns with 3 isolation levels (RLS, schema-per-tenant, DB-per-tenant), (6) Enhanced local development tools including unified dashboard, one-command setup, offline mode with service mocking, and unified log aggregation, (7) Production-ready deployment patterns including multi-region, blue-green deployments, disaster recovery procedures, and compliance configurations (SOC2, HIPAA, GDPR). The enhancement maintains backward compatibility with 012-saas-starter while supporting 100+ valid technology combinations, achieving 80% test coverage, and delivering measurable improvements: 60% reduction in time-to-production (up from 50%), 92% developer setup completion without support (up from 90%), and support for 10,000 concurrent users (up from 1,000).

## Technical Context

**Language/Version**: Python 3.11+ (template layer, validation scripts, migration tools), TypeScript 5.6+ (config builder UI, generated apps when Node runtime), JavaScript (Node 20 LTS for Next.js 16/Remix 2.x runtimes)  
**Primary Dependencies**: Copier ≥9.0 (template engine), Jinja2 ≥3.1 (templating), uv ≥0.4 (Python packaging), pnpm ≥8 (Node packaging), Next.js 16 or Remix 2.x (runtime frameworks), React 19.2 (UI framework), all expanded integration SDKs (Clerk/Auth.js/WorkOS/Supabase Auth, Stripe/Paddle, various search/cache/CMS providers), Ink ≥4 (CLI TUI), Vite ≥5 (config builder), Playwright ≥1.40 (E2E testing), k6 or Artillery (load testing)  
**Storage**: PostgreSQL via Neon/Supabase/PlanetScale/CockroachDB (user choice), persisted via Prisma or Drizzle ORM (user choice), Redis/Upstash/Cloudflare KV (cache layer, user choice), Algolia/Meilisearch/Typesense (search layer, user choice), Cloudflare R2/Supabase Storage/AWS S3/UploadThing (object storage, user choice)  
**Testing**: pytest (template validation), Vitest/Jest (generated app unit tests), Playwright (E2E tests), k6/Artillery (load tests), OWASP ZAP (security tests), axe-core (accessibility tests), Percy/Chromatic (visual regression), contract testing for all integrations  
**Target Platform**: Vercel or Cloudflare Pages/Workers (user choice for hosting), GitHub Actions or Cloudflare CI (user choice for CI/CD), multi-region deployment support, edge compute compatibility  
**Project Type**: Copier template module enhancement generating full-stack web applications with optional monorepo structure, multi-tenant architecture patterns, and production deployment configurations  
**Performance Goals**: Template rendering <7min (expanded from 5min due to increased scope), config builder loads <2sec, compatibility validation <500ms, generated app startup <3min (expanded from 2min), deployment <12min (expanded from 10min), E2E test suite <3min, fixture generation 1000+ records <15sec (expanded from 10sec), search queries <100ms p95, cache hit rates >85%, API responses <200ms p95  
**Constraints**: Support minimum 100 valid technology combinations (up from 26), maintain deterministic generation (same answers = identical output), backward compatibility with 012-saas-starter configurations, all combinations must pass quality checks, 95% deployment success rate, 92% developer setup completion without support, 80% minimum test coverage (up from 70%)  
**Scale/Scope**: 21 infrastructure categories (14 original + 7 new) with 3-4 options each = 80+ total integrations to implement, 200+ Jinja2 templates across all combinations, migration tool supporting technology swaps for all categories, config builder (web UI + CLI TUI), seeded fixtures for 10+ domain entities (expanded from 5), comprehensive test coverage (80% minimum, 95% target for strict profile), documentation for all 80+ technologies, runbooks for 20+ operational scenarios, compliance configurations for 3+ regulatory frameworks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASS (with justified complexity - builds on approved 012-saas-starter foundation)

### Principle Verification

✅ **Module Sovereignty** - PASS
- Feature is ENHANCEMENT to optional module (saas_starter_module flag from 012-saas-starter)
- Maintains backward compatibility - existing 012 configurations still work
- Self-contained with no dependencies on other optional modules
- Independent documentation in enhanced `docs/modules/saas-starter.md.jinja`
- Smoke tests prove standalone functionality across all 100+ combinations
- Migration tools enable technology swaps without affecting other modules

✅ **Deterministic Generation** - PASS
- Same Copier answers produce identical output (no timestamps, random values, system paths)
- Technology selections are deterministic based on user choices (expanded options still deterministic)
- Pinned dependency versions ensure reproducibility across all 80+ integrations
- CI validation via enhanced `render_matrix.py` confirms determinism for all combinations
- Configuration builder exports deterministic `copier-answers.yml` files
- Migration tool produces deterministic diffs and transformations

⚠️ **Minimal Baseline** - CONDITIONAL PASS (Same justification as 012-saas-starter)
- Feature is OPTIONAL ENHANCEMENT - baseline render unaffected when saas_starter_module disabled
- When enabled, generates 200+ files (up from 100+) with 80+ integrations (up from 28)
- Justification: Enterprise SaaS applications inherently require expanded infrastructure
  - Search (Algolia/Meilisearch/Typesense) - essential for user-facing content discovery
  - Cache (Redis/Upstash/KV) - required for performance at scale (10K+ concurrent users)
  - Feature flags (LaunchDarkly/PostHog/GrowthBook) - standard practice for controlled rollouts
  - CMS (Contentful/Sanity/Payload/Strapi) - needed for marketing pages and documentation
  - Usage metering - required for usage-based billing models
  - Secrets management - production security requirement
  - Multi-tenant isolation - B2B SaaS standard architecture
- Users explicitly opt-in knowing they're generating enterprise-grade full-stack application
- No bloat added to disabled baseline or basic saas-starter configurations
- Enhanced tools (config builder, migration) are optional conveniences, not requirements

✅ **Quality Integration** - PASS
- All generated code integrates with ruff, mypy, pylint, pytest, eslint, typescript
- Passes `QUALITY_PROFILE=standard make quality` and `QUALITY_PROFILE=strict` for enhanced mode
- Python 3.11, 3.12, 3.13 compatibility enforced
- Node 20 LTS compatibility enforced for TypeScript/JavaScript
- CI workflows (`riso-quality.yml`, `riso-matrix.yml`) included in all generated projects
- Enhanced test coverage requirements: 80% minimum (up from 70%), 95% target for strict
- Additional test types: load tests (k6/Artillery), security tests (OWASP ZAP), accessibility (axe-core)

✅ **Test-First Development** - PASS
- Template validation tests written first (test rendering logic for all combinations)
- Generated applications include comprehensive test suites (unit + integration + E2E + load + security)
- Migration tool includes pre/post migration test validation
- Config builder includes validation tests for compatibility rules
- Unit tests for business logic, integration tests for all 80+ services, E2E for critical flows
- 80% minimum coverage enforced (up from 70%), 95% target for strict profile
- Chaos engineering tests validate graceful degradation

✅ **Documentation Standards** - PASS
- Generated projects include enhanced README, quickstart, module docs, runbooks, ADRs
- All documentation auto-generated from Jinja2 templates (`*.md.jinja`)
- Working code examples for each of 80+ integrations
- Links to service-specific external documentation
- Architecture decision records (ADRs) document technology choice rationale
- Troubleshooting guides for each service integration
- Cost optimization guides for infrastructure spend
- Migration guides for technology swaps
- Compliance documentation for SOC2, HIPAA, GDPR

✅ **Technology Consistency** - PASS
- Template layer uses Python 3.11+ with uv (consistent with Riso baseline)
- Generated apps use approved tech stack (Node 20 LTS + pnpm when Node track)
- Quality tools: ruff + mypy + pylint + pytest + eslint + typescript (no alternatives)
- CI: GitHub Actions or Cloudflare CI (user choice from approved options)
- Containers: Docker with multi-stage builds (when container module enabled)
- All new integrations use officially supported SDKs and APIs
- Config builder uses React 19.2 + Vite (approved Riso frontend stack)
- Migration tool uses Python 3.11+ with uv (consistent with template layer)

### Complexity Justification Required

This enhancement introduces additional complexity beyond 012-saas-starter that requires justification:

| Concern | Justification | Mitigation |
|---------|--------------|------------|
| 80+ technology integrations (up from 28) | Enterprise SaaS requires expanded infrastructure: search for content discovery, cache for scale, feature flags for controlled rollouts, CMS for marketing content, usage metering for modern billing, secrets management for security, multi-tenant patterns for B2B | Maintains 3-4 carefully curated options per category (not unlimited); compatibility validation prevents invalid combinations; comprehensive integration tests for all combinations; documentation for each integration |
| 200+ Jinja2 templates (up from 100+) | Each new technology requires service-specific integration code; expanded options require conditional templates; multi-tenant patterns need isolation-specific templates; migration tool needs transformation templates | Shared template partials for common patterns; template inheritance reduces duplication; automated template testing ensures correctness; template validation in CI prevents drift |
| Config builder (new web UI + CLI TUI) | Complexity of 100+ technology combinations makes manual selection error-prone; real-time compatibility validation prevents invalid configurations; cost estimates prevent budget overruns; architecture diagrams improve understanding | Config builder is optional convenience tool; users can still use manual Copier prompts; builder generates standard copier-answers.yml files; builder itself is well-tested separate component |
| Migration tool (new capability) | Production applications need ability to swap technologies as requirements evolve; manual migration is error-prone and time-consuming; automated code analysis ensures completeness | Migration tool is optional post-generation convenience; uses three-way merge for safety; includes dry-run mode; rollback capability prevents data loss; comprehensive pre/post migration tests |
| Multi-tenant architecture patterns (new capability) | B2B SaaS requires tenant isolation; row-level security, schema-per-tenant, database-per-tenant are proven patterns; per-tenant billing and feature flags are standard B2B requirements | Multi-tenant mode is optional architecture choice; clear documentation on when to use; isolation levels match scale requirements; proven PostgreSQL RLS patterns; comprehensive security testing |
| Production deployment patterns (new capability) | Enterprise applications require multi-region deployment, blue-green deployments, disaster recovery; compliance (SOC2/HIPAA/GDPR) is mandatory for regulated industries | Production patterns are optional enhancements; infrastructure-as-code templates are standard practice; runbooks document procedures; compliance configurations provide frameworks (require legal review) |
| Enhanced local dev tools (dashboard, one-command setup, offline mode) | Developers spend significant time on environment setup; context switching between services reduces productivity; offline development enables work without internet | Dev tools are optional conveniences; docker-compose fallback for simpler setups; service mocking uses standard patterns; unified dashboard uses proven monitoring approaches |

**Approval**: These complexities are justified because:
1. Feature remains optional (baseline unaffected when disabled)
2. Builds on proven 012-saas-starter foundation (not starting from scratch)
3. Users explicitly opt-in to enterprise-grade features
4. Alternative (manual integration + configuration) takes 10-100x longer
5. Success criteria show measurable value:
   - SC-027: "Reduce time to production by 60%" (up from 50% in 012)
   - SC-021: "92% developer setup completion without support" (up from 90%)
   - SC-016: "Handle 10,000 concurrent users" (up from 1,000)
6. All complexity serves specific, documented user requirements from specification
7. Backward compatibility preserved - existing 012 configurations work unchanged
8. Incremental adoption possible - users can enable only needed enhancements

## Project Structure

### Documentation (this feature)

```text
specs/017-saas-starter-enhancement/
├── spec.md                      # Feature specification (completed)
├── plan.md                      # This file (in progress)
├── research.md                  # Phase 0 output (to be generated)
├── data-model.md                # Phase 1 output (to be generated)
├── quickstart.md                # Phase 1 output (to be generated)
├── contracts/                   # Phase 1 output (to be generated)
│   ├── copier-prompts.yml              # Enhanced prompts for 21 categories
│   ├── integration-apis.md             # API contracts for 80+ integrations
│   ├── compatibility-matrix.md         # Valid combination rules
│   ├── config-builder-api.md           # Config builder REST API spec
│   ├── migration-tool-cli.md           # Migration tool command interface
│   └── multi-tenant-patterns.md        # Multi-tenant architecture contracts
├── tasks.md                     # Phase 2 output (created by /speckit.tasks)
└── checklists/
    └── requirements.md          # Spec quality checklist (completed)
```

### Source Code (Riso template repository root)

```text
template/
├── copier.yml                          # Enhanced with 21 categories, 3-4 options each
├── files/
│   ├── shared/
│   │   ├── docs/
│   │   │   └── modules/
│   │   │       ├── saas-starter.md.jinja        # Enhanced module documentation
│   │   │       ├── saas-config-builder.md.jinja # Config builder guide
│   │   │       ├── saas-migration.md.jinja      # Migration guide
│   │   │       └── saas-multi-tenant.md.jinja   # Multi-tenant guide
│   │   ├── saas-starter/                        # Enhanced directory
│   │   │   ├── config.ts.jinja                  # Enhanced configuration file
│   │   │   ├── README.md.jinja                  # Enhanced feature README
│   │   │   ├── ARCHITECTURE.md.jinja            # Architecture diagrams
│   │   │   └── ADR/                             # Architecture decision records
│   │   │       ├── 001-database-choice.md.jinja
│   │   │       ├── 002-auth-provider.md.jinja
│   │   │       └── ...
│   │   └── .github/
│   │       └── workflows/
│   │           ├── saas-load-test.yml.jinja     # Load testing workflow
│   │           ├── saas-security-scan.yml.jinja # Security testing workflow
│   │           └── saas-deploy-prod.yml.jinja   # Production deployment workflow
│   ├── python/
│   │   └── saas/
│   │       ├── __init__.py.jinja
│   │       ├── observability/                   # Enhanced observability
│   │       ├── fixtures/                        # Expanded fixture support
│   │       ├── factories/                       # Faker integration
│   │       ├── migrations/                      # Migration tool core logic
│   │       │   ├── analyzer.py.jinja
│   │       │   ├── planner.py.jinja
│   │       │   ├── executor.py.jinja
│   │       │   └── rollback.py.jinja
│   │       └── tests/
│   │           ├── unit/
│   │           ├── integration/
│   │           ├── e2e/
│   │           ├── load/                        # k6/Artillery load tests
│   │           ├── security/                    # OWASP ZAP security tests
│   │           └── chaos/                       # Chaos engineering tests
│   └── node/
│       └── saas/
│           ├── config-builder/                  # NEW: Visual config builder
│           │   ├── web/                         # Web UI version
│           │   │   ├── src/
│           │   │   │   ├── components/
│           │   │   │   │   ├── CategorySelector.tsx.jinja
│           │   │   │   │   ├── CompatibilityValidator.tsx.jinja
│           │   │   │   │   ├── CostEstimator.tsx.jinja
│           │   │   │   │   ├── ArchitectureDiagram.tsx.jinja
│           │   │   │   │   └── ConfigExporter.tsx.jinja
│           │   │   │   ├── lib/
│           │   │   │   │   ├── compatibility.ts.jinja
│           │   │   │   │   ├── cost-calculator.ts.jinja
│           │   │   │   │   └── diagram-generator.ts.jinja
│           │   │   │   ├── App.tsx.jinja
│           │   │   │   └── main.tsx.jinja
│           │   │   ├── package.json.jinja
│           │   │   └── vite.config.ts.jinja
│           │   └── cli/                         # CLI TUI version
│           │       ├── src/
│           │       │   ├── ui.tsx.jinja         # Ink-based TUI
│           │       │   └── index.ts.jinja
│           │       └── package.json.jinja
│           ├── runtime/
│           │   ├── nextjs/                      # Enhanced Next.js templates
│           │   │   ├── app/
│           │   │   │   ├── (auth)/              # Auth routes
│           │   │   │   ├── (dashboard)/         # Dashboard routes
│           │   │   │   ├── (admin)/             # Admin portal (multi-tenant)
│           │   │   │   ├── (marketing)/         # Marketing pages (CMS)
│           │   │   │   └── api/
│           │   │   │       ├── webhooks/        # Webhook handlers
│           │   │   │       ├── admin/           # Admin API
│           │   │   │       └── public/          # Public API
│           │   │   ├── middleware.ts.jinja      # Enhanced middleware
│           │   │   ├── instrumentation.ts.jinja # OpenTelemetry setup
│           │   │   └── next.config.js.jinja     # Enhanced Next.js config
│           │   └── remix/                       # Enhanced Remix templates
│           │       ├── app/
│           │       │   ├── routes/
│           │       │   ├── utils/
│           │       │   └── entry.server.tsx.jinja
│           │       └── remix.config.js.jinja
│           ├── integrations/                    # 80+ service integrations
│           │   ├── auth/                        # 4 options (expanded from 2)
│           │   │   ├── clerk/
│           │   │   ├── authjs/
│           │   │   ├── workos/                  # NEW
│           │   │   └── supabase-auth/           # NEW
│           │   ├── database/                    # 4 options (expanded from 2)
│           │   │   ├── neon/
│           │   │   ├── supabase/
│           │   │   ├── planetscale/             # NEW
│           │   │   └── cockroachdb/             # NEW
│           │   ├── storage/                     # 4 options (expanded from 2)
│           │   │   ├── r2/
│           │   │   ├── supabase-storage/
│           │   │   ├── s3/                      # NEW
│           │   │   └── uploadthing/             # NEW
│           │   ├── email/                       # 4 options (expanded from 2)
│           │   │   ├── resend/
│           │   │   ├── postmark/
│           │   │   ├── sendgrid/                # NEW
│           │   │   └── ses/                     # NEW
│           │   ├── ai/                          # 4 options (expanded from 2)
│           │   │   ├── openai/
│           │   │   ├── anthropic/
│           │   │   ├── gemini/                  # NEW
│           │   │   └── ollama/                  # NEW (local LLMs)
│           │   ├── search/                      # NEW CATEGORY (3 options)
│           │   │   ├── algolia/
│           │   │   │   ├── client.ts.jinja
│           │   │   │   ├── indexing.ts.jinja
│           │   │   │   └── search.ts.jinja
│           │   │   ├── meilisearch/
│           │   │   │   ├── client.ts.jinja
│           │   │   │   ├── indexing.ts.jinja
│           │   │   │   └── search.ts.jinja
│           │   │   └── typesense/
│           │   │       ├── client.ts.jinja
│           │   │       ├── indexing.ts.jinja
│           │   │       └── search.ts.jinja
│           │   ├── cache/                       # NEW CATEGORY (3 options)
│           │   │   ├── redis/                   # Upstash Redis
│           │   │   │   ├── client.ts.jinja
│           │   │   │   ├── patterns.ts.jinja   # Caching patterns
│           │   │   │   └── distributed-lock.ts.jinja
│           │   │   ├── cloudflare-kv/
│           │   │   │   ├── client.ts.jinja
│           │   │   │   └── patterns.ts.jinja
│           │   │   └── vercel-kv/
│           │   │       ├── client.ts.jinja
│           │   │       └── patterns.ts.jinja
│           │   ├── feature-flags/               # NEW CATEGORY (3 options)
│           │   │   ├── launchdarkly/
│           │   │   │   ├── client.ts.jinja
│           │   │   │   ├── provider.tsx.jinja
│           │   │   │   └── hooks.ts.jinja
│           │   │   ├── posthog-flags/
│           │   │   │   ├── client.ts.jinja
│           │   │   │   └── hooks.ts.jinja
│           │   │   └── growthbook/
│           │   │       ├── client.ts.jinja
│           │   │       └── hooks.ts.jinja
│           │   ├── cms/                         # NEW CATEGORY (4 options)
│           │   │   ├── contentful/
│           │   │   │   ├── client.ts.jinja
│           │   │   │   ├── types.ts.jinja
│           │   │   │   └── components/
│           │   │   ├── sanity/
│           │   │   │   ├── client.ts.jinja
│           │   │   │   ├── schemas/
│           │   │   │   └── studio/
│           │   │   ├── payload/
│           │   │   │   ├── payload.config.ts.jinja
│           │   │   │   └── collections/
│           │   │   └── strapi/
│           │   │       ├── client.ts.jinja
│           │   │       └── types.ts.jinja
│           │   ├── usage-metering/              # NEW CATEGORY (3 options)
│           │   │   ├── stripe-metering/
│           │   │   │   ├── client.ts.jinja
│           │   │   │   ├── meter.ts.jinja
│           │   │   │   └── reporting.ts.jinja
│           │   │   ├── moesif/
│           │   │   │   ├── client.ts.jinja
│           │   │   │   └── tracking.ts.jinja
│           │   │   └── amberflo/
│           │   │       ├── client.ts.jinja
│           │   │       └── metering.ts.jinja
│           │   ├── secrets/                     # NEW CATEGORY (3 options)
│           │   │   ├── infisical/
│           │   │   │   ├── client.ts.jinja
│           │   │   │   └── sync.ts.jinja
│           │   │   ├── doppler/
│           │   │   │   ├── client.ts.jinja
│           │   │   │   └── sync.ts.jinja
│           │   │   └── aws-secrets-manager/
│           │   │       ├── client.ts.jinja
│           │   │       └── sync.ts.jinja
│           │   ├── error-tracking/              # NEW CATEGORY (3 options - enhanced)
│           │   │   ├── sentry-enhanced/         # Enhanced Sentry config
│           │   │   ├── rollbar/
│           │   │   └── bugsnag/
│           │   ├── billing/                     # Existing (maintained)
│           │   │   ├── stripe/
│           │   │   └── paddle/
│           │   ├── jobs/                        # Existing (maintained)
│           │   │   ├── triggerdev/
│           │   │   └── inngest/
│           │   ├── analytics/                   # Existing (maintained)
│           │   │   ├── posthog/
│           │   │   └── amplitude/
│           │   ├── observability/               # Existing (enhanced)
│           │   │   ├── sentry.ts.jinja
│           │   │   ├── datadog.ts.jinja
│           │   │   ├── otel.ts.jinja
│           │   │   └── dashboards/              # Pre-built dashboard templates
│           │   │       ├── saas-kpis.json.jinja
│           │   │       ├── performance.json.jinja
│           │   │       └── errors.json.jinja
│           │   ├── orm/                         # Existing (maintained)
│           │   │   ├── prisma/
│           │   │   └── drizzle/
│           │   └── enterprise/                  # Existing (maintained)
│           │       └── workos/
│           ├── multi-tenant/                    # NEW: Multi-tenant patterns
│           │   ├── isolation/
│           │   │   ├── rls/                     # Row-level security
│           │   │   │   ├── policies.sql.jinja
│           │   │   │   └── middleware.ts.jinja
│           │   │   ├── schema-per-tenant/       # Schema isolation
│           │   │   │   ├── provisioning.ts.jinja
│           │   │   │   └── routing.ts.jinja
│           │   │   └── db-per-tenant/           # Database isolation
│           │   │       ├── provisioning.ts.jinja
│           │   │       └── connection-pool.ts.jinja
│           │   ├── provisioning/
│           │   │   ├── api.ts.jinja
│           │   │   ├── workflow.ts.jinja
│           │   │   └── cleanup.ts.jinja
│           │   ├── subdomain-routing/
│           │   │   ├── middleware.ts.jinja
│           │   │   └── resolver.ts.jinja
│           │   ├── admin-portal/
│           │   │   ├── components/
│           │   │   │   ├── TenantList.tsx.jinja
│           │   │   │   ├── TenantForm.tsx.jinja
│           │   │   │   └── TenantUsage.tsx.jinja
│           │   │   └── api/
│           │   │       └── tenants.ts.jinja
│           │   └── billing-integration/
│           │       ├── per-tenant-metering.ts.jinja
│           │       └── invoicing.ts.jinja
│           ├── production/                      # NEW: Production patterns
│           │   ├── multi-region/
│           │   │   ├── terraform/               # IaC templates
│           │   │   │   ├── vercel.tf.jinja
│           │   │   │   └── cloudflare.tf.jinja
│           │   │   ├── dns-failover.ts.jinja
│           │   │   └── health-checks.ts.jinja
│           │   ├── blue-green/
│           │   │   ├── deployment.yml.jinja
│           │   │   ├── traffic-shift.ts.jinja
│           │   │   └── rollback.ts.jinja
│           │   ├── backup-restore/
│           │   │   ├── backup.sh.jinja
│           │   │   ├── restore.sh.jinja
│           │   │   └── verification.ts.jinja
│           │   ├── disaster-recovery/
│           │   │   ├── runbook.md.jinja
│           │   │   ├── rto-rpo.md.jinja
│           │   │   └── procedures/
│           │   └── compliance/
│           │       ├── soc2/
│           │       │   ├── controls.md.jinja
│           │       │   └── audit-logs.ts.jinja
│           │       ├── hipaa/
│           │       │   ├── baa-requirements.md.jinja
│           │       │   └── encryption.ts.jinja
│           │       └── gdpr/
│           │           ├── data-residency.ts.jinja
│           │           ├── right-to-deletion.ts.jinja
│           │           └── consent-management.ts.jinja
│           ├── dev-tools/                       # NEW: Enhanced local dev tools
│           │   ├── dashboard/
│           │   │   ├── src/
│           │   │   │   ├── components/
│           │   │   │   │   ├── ServiceStatus.tsx.jinja
│           │   │   │   │   ├── LogViewer.tsx.jinja
│           │   │   │   │   └── MetricsPanel.tsx.jinja
│           │   │   │   └── App.tsx.jinja
│           │   │   └── package.json.jinja
│           │   ├── setup/
│           │   │   ├── one-command-setup.sh.jinja
│           │   │   ├── validate-env.ts.jinja
│           │   │   └── seed-fixtures.ts.jinja
│           │   ├── offline-mode/
│           │   │   ├── mocks/
│           │   │   │   ├── auth-mock.ts.jinja
│           │   │   │   ├── billing-mock.ts.jinja
│           │   │   │   ├── ai-mock.ts.jinja
│           │   │   │   └── ...
│           │   │   └── enable-offline.ts.jinja
│           │   ├── log-aggregator/
│           │   │   ├── correlate.ts.jinja
│           │   │   ├── format.ts.jinja
│           │   │   └── viewer.tsx.jinja
│           │   └── docker-compose.yml.jinja     # Local service orchestration
│           ├── fixtures/                        # Enhanced fixtures (10+ entities)
│           │   ├── users.ts.jinja
│           │   ├── organizations.ts.jinja
│           │   ├── subscriptions.ts.jinja
│           │   ├── invoices.ts.jinja
│           │   ├── usage-records.ts.jinja
│           │   ├── feature-flags.ts.jinja
│           │   ├── content-pages.ts.jinja       # CMS fixtures
│           │   ├── search-index.ts.jinja        # Search fixtures
│           │   └── ...
│           ├── factories/                       # Faker integration
│           │   ├── index.ts.jinja
│           │   ├── user-factory.ts.jinja
│           │   ├── org-factory.ts.jinja
│           │   └── ...
│           ├── hosting/                         # Existing (maintained)
│           │   ├── vercel/
│           │   └── cloudflare/
│           └── tests/
│               ├── unit/
│               ├── integration/                 # Enhanced with all new integrations
│               │   ├── search.spec.ts.jinja
│               │   ├── cache.spec.ts.jinja
│               │   ├── feature-flags.spec.ts.jinja
│               │   ├── cms.spec.ts.jinja
│               │   ├── usage-metering.spec.ts.jinja
│               │   ├── secrets.spec.ts.jinja
│               │   └── ...
│               ├── e2e/
│               │   ├── auth.spec.ts.jinja
│               │   ├── billing.spec.ts.jinja
│               │   ├── dashboard.spec.ts.jinja
│               │   ├── multi-tenant.spec.ts.jinja  # NEW
│               │   └── ...
│               ├── load/                        # NEW: Load tests
│               │   ├── k6/
│               │   │   ├── api-load.js.jinja
│               │   │   └── scenarios/
│               │   └── artillery/
│               │       └── load-test.yml.jinja
│               ├── security/                    # NEW: Security tests
│               │   ├── owasp-zap.yml.jinja
│               │   └── scan-results/
│               ├── accessibility/               # NEW: a11y tests
│               │   └── axe-tests.spec.ts.jinja
│               └── chaos/                       # NEW: Chaos engineering
│                   ├── service-failures.spec.ts.jinja
│                   └── network-issues.spec.ts.jinja

scripts/
├── ci/
│   ├── validate_saas_combinations.py            # Enhanced for 100+ combinations
│   ├── render_saas_samples.py                   # Enhanced sample generation
│   ├── validate_migration_tool.py               # NEW: Migration tool validation
│   └── validate_config_builder.py               # NEW: Config builder validation
├── saas/
│   ├── compatibility_matrix.py                  # Enhanced compatibility validation
│   ├── cost_calculator.py                       # NEW: Cost estimation engine
│   └── diagram_generator.py                     # NEW: Architecture diagram generator
└── migration/                                    # NEW: Migration tool scripts
    ├── analyze.py                               # Codebase analysis
    ├── plan.py                                  # Migration planning
    ├── execute.py                               # Migration execution
    └── rollback.py                              # Rollback procedures

samples/
└── saas-starter-enhanced/                       # NEW: Enhanced samples
    ├── edge-optimized-v2/                       # Cloudflare + edge stack
    ├── enterprise-ready-v2/                     # Multi-tenant + compliance
    ├── all-in-one-v2/                           # Supabase + all-in-one
    ├── search-heavy/                            # Algolia + content-rich
    ├── ai-powered/                              # OpenAI + AI-first features
    └── multi-region-prod/                       # Multi-region + blue-green
```

**Structure Decision**: This enhancement builds on the proven 012-saas-starter structure while adding significant new capabilities organized into logical groupings:

1. **Config Builder** (`config-builder/`) - New standalone tool with web UI and CLI TUI versions
2. **Expanded Integrations** (`integrations/`) - 80+ integrations organized by category
3. **Multi-Tenant Patterns** (`multi-tenant/`) - New architecture patterns for B2B SaaS
4. **Production Patterns** (`production/`) - New enterprise deployment and compliance patterns
5. **Dev Tools** (`dev-tools/`) - New developer experience enhancements
6. **Enhanced Testing** (`tests/`) - New test categories (load, security, accessibility, chaos)

The structure maintains backward compatibility with 012-saas-starter while providing clear separation for new capabilities.

## Complexity Tracking

> **Filled because Constitution Check identified justified complexities**

| Complexity Item | Why Needed | Simpler Alternative Rejected Because |
|-----------------|------------|-------------------------------------|
| 80+ technology integrations | Enterprise SaaS requires expanded infrastructure beyond original 28: search, cache, feature flags, CMS, metering, secrets | Binary choice (2 options) insufficient for enterprise needs; users need 3-4 well-supported options to match specific requirements (cost, scale, compliance); limiting to 2 forces users into suboptimal choices |
| 200+ Jinja2 templates | Each technology has service-specific patterns; multi-tenant needs isolation-specific templates; conditional rendering for valid combinations | Generic templates sacrifice type safety and developer experience; each SDK has unique patterns; attempting to abstract further creates unmaintainable mega-templates |
| Config builder (web UI + CLI TUI) | 100+ combinations make manual selection error-prone; real-time validation prevents wasted time; cost estimates prevent budget overruns | Manual Copier prompts lead to invalid combinations discovered after generation; no way to visualize architecture or estimate costs before committing; users waste hours on trial-and-error |
| Migration tool | Production apps need technology swaps as requirements evolve; automated analysis ensures completeness; manual migration is error-prone | Manual migration requires deep template knowledge; users break applications attempting swaps; no rollback on failures; migrations take days instead of minutes |
| Multi-tenant architecture | B2B SaaS standard requirement; tenant isolation mandatory for security/compliance; proven patterns prevent reinvention | Implementing multi-tenancy from scratch takes weeks; security vulnerabilities common in custom implementations; proven RLS/schema/DB patterns are industry standard |
| Production deployment patterns | Enterprise requires multi-region, blue-green, DR; compliance (SOC2/HIPAA/GDPR) mandatory for regulated industries | Omitting production patterns leaves users unprepared for scale; implementing multi-region/blue-green from scratch takes weeks; compliance configurations require specialized knowledge |
| Enhanced dev tools | Developers spend hours on environment setup and context switching between services | Manual service management is error-prone; missing environment variables discovered at runtime; debugging across multiple service logs is time-consuming; offline development impossible without mocks |

**All complexities justified per Constitution approval in section above. No unjustified violations.**
