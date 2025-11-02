# Tasks: SaaS Starter Template

**Feature**: 012-saas-starter  
**Input**: Design documents from `/workspaces/riso/specs/012-saas-starter/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested in specification - TESTS OMITTED from task list

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format Convention

All tasks follow strict format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Task can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4) - REQUIRED for story phases
- **File paths**: All paths relative to Riso template repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project structure and base template configuration

- [ ] T001 Create directory structure template/files/shared/saas-starter/ for module files
- [ ] T002 Create directory structure template/files/node/saas/ for Node.js-specific templates
- [ ] T003 [P] Create saas-starter module documentation in template/files/shared/docs/modules/saas-starter.md.jinja
- [ ] T004 [P] Add SaaS starter prompts to template/copier.yml from contracts/copier-prompts.yml
- [ ] T005 [P] Create validation script scripts/ci/validate_saas_combinations.py for testing all 26 technology combinations
- [ ] T006 [P] Create render script scripts/saas/render_saas_samples.py for generating sample combinations
- [ ] T007 Create sample answer files in samples/saas-starter/ directory for recommended stacks

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core template infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Implement pre-generation validation hook in template/hooks/pre_gen_project.py with compatibility checking from contracts/validation-rules.md
- [ ] T009 Implement post-generation setup hook in template/hooks/post_gen_project.py with metadata recording and dependency installation
- [ ] T010 [P] Create base Jinja2 macro library in template/files/shared/saas-starter/_macros.jinja for reusable template components
- [ ] T011 [P] Create saas-starter.config.ts.jinja template in template/files/shared/saas-starter/ to document user selections
- [ ] T012 [P] Create .env.example.jinja template in template/files/shared/saas-starter/ with all required environment variables
- [ ] T013 Create compatibility matrix validation in scripts/saas/compatibility_matrix.py implementing ERROR/WARNING/INFO rules from contracts/validation-rules.md
- [ ] T014 Create README.md.jinja template in template/files/shared/saas-starter/ for generated projects

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Select and Generate SaaS Stack Configuration (Priority: P1) 🎯 MVP

**Goal**: Enable developers to render a complete SaaS application by making binary choices across 14 infrastructure categories

**Independent Test**: Run Copier with saas_starter_module=enabled, make all selections, verify working application generated with all integrations functional

### Runtime Framework Templates (US1)

- [ ] T015 [P] [US1] Create Next.js 16 base template structure in template/files/node/saas/runtime/nextjs/app/
- [ ] T016 [P] [US1] Create Next.js middleware.ts.jinja in template/files/node/saas/runtime/nextjs/ for auth and observability
- [ ] T017 [P] [US1] Create Next.js next.config.js.jinja in template/files/node/saas/runtime/nextjs/
- [ ] T018 [P] [US1] Create Remix 2.x base template structure in template/files/node/saas/runtime/remix/app/
- [ ] T019 [P] [US1] Create Remix root.tsx.jinja in template/files/node/saas/runtime/remix/app/ with providers
- [ ] T020 [P] [US1] Create Remix remix.config.js.jinja in template/files/node/saas/runtime/remix/

### Database Schema Templates (US1)

- [ ] T021 [P] [US1] Create Prisma schema.prisma.jinja in template/files/node/saas/integrations/orm/prisma/ with entities from data-model.md (User, Organization, Subscription, etc.)
- [ ] T022 [P] [US1] Create Drizzle schema.ts.jinja in template/files/node/saas/integrations/orm/drizzle/ with same entities
- [ ] T023 [US1] Create database connection templates lib/database/client.ts.jinja with Neon and Supabase variants

### Authentication Integration Templates (US1)

- [ ] T024 [P] [US1] Create Clerk integration in template/files/node/saas/integrations/auth/clerk/ with middleware.ts.jinja and setup.ts.jinja
- [ ] T025 [P] [US1] Create Auth.js integration in template/files/node/saas/integrations/auth/authjs/ with auth.config.ts.jinja
- [ ] T026 [P] [US1] Create auth helper functions lib/auth/helpers.ts.jinja with session management

### Billing Integration Templates (US1)

- [ ] T027 [P] [US1] Create Stripe integration in template/files/node/saas/integrations/billing/stripe/ with client.ts.jinja and webhooks.ts.jinja
- [ ] T028 [P] [US1] Create Paddle integration in template/files/node/saas/integrations/billing/paddle/ with client.ts.jinja and webhooks.ts.jinja
- [ ] T029 [US1] Create billing service lib/billing/service.ts.jinja with subscription management

### Background Jobs Integration Templates (US1)

- [ ] T030 [P] [US1] Create Trigger.dev v4 integration in template/files/node/saas/integrations/jobs/triggerdev/ with example jobs
- [ ] T031 [P] [US1] Create Inngest integration in template/files/node/saas/integrations/jobs/inngest/ with example functions
- [ ] T032 [US1] Create job helpers lib/jobs/helpers.ts.jinja with queue management

### Email Integration Templates (US1)

- [ ] T033 [P] [US1] Create Resend integration in template/files/node/saas/integrations/email/resend/ with client.ts.jinja
- [ ] T034 [P] [US1] Create React Email templates in template/files/node/saas/integrations/email/resend/templates/ (welcome.tsx.jinja, etc.)
- [ ] T035 [P] [US1] Create Postmark integration in template/files/node/saas/integrations/email/postmark/ with client.ts.jinja
- [ ] T036 [US1] Create email service lib/email/service.ts.jinja with sending logic

### Analytics Integration Templates (US1)

- [ ] T037 [P] [US1] Create PostHog integration in template/files/node/saas/integrations/analytics/posthog/ with client.ts.jinja
- [ ] T038 [P] [US1] Create Amplitude integration in template/files/node/saas/integrations/analytics/amplitude/ with client.ts.jinja
- [ ] T039 [US1] Create analytics helper lib/analytics/events.ts.jinja with event tracking

### AI Integration Templates (US1)

- [ ] T040 [P] [US1] Create OpenAI integration in template/files/node/saas/integrations/ai/openai/ with client.ts.jinja
- [ ] T041 [P] [US1] Create Anthropic integration in template/files/node/saas/integrations/ai/anthropic/ with client.ts.jinja
- [ ] T042 [US1] Create AI service lib/ai/service.ts.jinja with LLM abstraction

### Storage Integration Templates (US1)

- [ ] T043 [P] [US1] Create Cloudflare R2 integration in template/files/node/saas/integrations/storage/r2/ with client.ts.jinja
- [ ] T044 [P] [US1] Create Supabase Storage integration in template/files/node/saas/integrations/storage/supabase-storage/ with client.ts.jinja
- [ ] T045 [US1] Create storage service lib/storage/service.ts.jinja with file management

### Observability Integration Templates (US1)

- [ ] T046 [P] [US1] Create Sentry integration in template/files/node/saas/integrations/observability/sentry.ts.jinja with client and server configs
- [ ] T047 [P] [US1] Create Datadog integration in template/files/node/saas/integrations/observability/datadog.ts.jinja with APM setup
- [ ] T048 [P] [US1] Create OpenTelemetry integration in template/files/node/saas/integrations/observability/otel.ts.jinja with instrumentation
- [ ] T049 [US1] Create structured logging lib/observability/logger.ts.jinja with correlation IDs

### Hosting Configuration Templates (US1)

- [ ] T050 [P] [US1] Create Vercel configuration in template/files/node/saas/hosting/vercel/vercel.json.jinja
- [ ] T051 [P] [US1] Create Cloudflare configuration in template/files/node/saas/hosting/cloudflare/wrangler.toml.jinja

### CI/CD Workflow Templates (US1)

- [ ] T052 [P] [US1] Create GitHub Actions workflow in template/files/shared/.github/workflows/saas-deploy.yml.jinja for Vercel deployment
- [ ] T053 [P] [US1] Create Cloudflare CI workflow in template/files/node/saas/cicd/cloudflare-ci.yml.jinja for Pages/Workers deployment

### Environment Configuration (US1)

- [ ] T054 [US1] Create environment validation lib/env.ts.jinja using @t3-oss/env-nextjs with Zod schemas from contracts/validation-rules.md
- [ ] T055 [US1] Implement environment variable requirements for all 28 service integrations in lib/env.ts.jinja

### Package Configuration (US1)

- [ ] T056 [US1] Create package.json.jinja template in template/files/node/saas/ with conditional dependencies based on selections
- [ ] T057 [US1] Create tsconfig.json.jinja template in template/files/node/saas/ with TypeScript configuration

**Checkpoint**: User Story 1 complete - template can generate working SaaS applications with all integrations

---

## Phase 4: User Story 2 - Understand Technology Trade-offs (Priority: P2)

**Goal**: Provide clear guidance for each technology option so developers make informed decisions

**Independent Test**: Review Copier prompts during rendering and verify each option includes actionable use-when guidance

### Prompt Enhancement (US2)

- [ ] T058 [US2] Add detailed help text to all Copier prompts in template/copier.yml with use-when guidance from contracts/copier-prompts.yml
- [ ] T059 [US2] Create decision guide documentation in template/files/shared/docs/saas-starter-decisions.md.jinja explaining trade-offs

### Comparison Documentation (US2)

- [ ] T060 [P] [US2] Create runtime comparison docs in template/files/shared/docs/saas-starter-decisions.md.jinja (Next.js vs Remix section)
- [ ] T061 [P] [US2] Create hosting comparison docs in template/files/shared/docs/saas-starter-decisions.md.jinja (Vercel vs Cloudflare section)
- [ ] T062 [P] [US2] Create database comparison docs in template/files/shared/docs/saas-starter-decisions.md.jinja (Neon vs Supabase section)
- [ ] T063 [P] [US2] Create ORM comparison docs in template/files/shared/docs/saas-starter-decisions.md.jinja (Prisma vs Drizzle section)
- [ ] T064 [P] [US2] Create auth comparison docs in template/files/shared/docs/saas-starter-decisions.md.jinja (Clerk vs Auth.js section)
- [ ] T065 [P] [US2] Create billing comparison docs in template/files/shared/docs/saas-starter-decisions.md.jinja (Stripe vs Paddle section)
- [ ] T066 [P] [US2] Create jobs comparison docs in template/files/shared/docs/saas-starter-decisions.md.jinja (Trigger.dev vs Inngest section)
- [ ] T067 [P] [US2] Create email comparison docs in template/files/shared/docs/saas-starter-decisions.md.jinja (Resend vs Postmark section)
- [ ] T068 [P] [US2] Create analytics comparison docs in template/files/shared/docs/saas-starter-decisions.md.jinja (PostHog vs Amplitude section)
- [ ] T069 [P] [US2] Create AI comparison docs in template/files/shared/docs/saas-starter-decisions.md.jinja (OpenAI vs Anthropic section)
- [ ] T070 [P] [US2] Create storage comparison docs in template/files/shared/docs/saas-starter-decisions.md.jinja (R2 vs Supabase Storage section)

### Recommended Stacks Documentation (US2)

- [ ] T071 [US2] Document recommended stacks in template/files/shared/docs/saas-starter-decisions.md.jinja from contracts/validation-rules.md (Vercel Starter, Edge Optimized, All-in-One Platform, Enterprise Ready)
- [ ] T072 [US2] Update pre-generation hook to suggest matching recommended stack when user selections are 80%+ similar

**Checkpoint**: User Story 2 complete - developers can make informed technology decisions with clear guidance

---

## Phase 5: User Story 3 - Customize Configuration Post-Generation (Priority: P3)

**Goal**: Enable developers to understand and potentially migrate their technology choices after generation

**Independent Test**: Generate application, locate saas-starter.config.ts, verify it accurately documents all selections

### Configuration Documentation (US3)

- [ ] T073 [US3] Implement saas-starter.config.ts.jinja generation with all user selections from template/files/shared/saas-starter/saas-starter.config.ts.jinja
- [ ] T074 [US3] Add metadata section to config (version, generatedAt, copier version) in saas-starter.config.ts.jinja
- [ ] T075 [US3] Add technology selection details (id, label, useWhen) for all 14 categories in saas-starter.config.ts.jinja

### Migration Guidance (US3)

- [ ] T076 [P] [US3] Create migration guide documentation in template/files/shared/docs/saas-starter-migration.md.jinja
- [ ] T077 [P] [US3] Add service-specific migration sections for each of the 14 categories in docs/saas-starter-migration.md.jinja
- [ ] T078 [US3] Create checklist for post-generation technology changes in docs/saas-starter-migration.md.jinja

### Metadata Recording (US3)

- [ ] T079 [US3] Implement metadata recording in post-generation hook template/hooks/post_gen_project.py writing to .saas-starter/metadata.json
- [ ] T080 [US3] Add timestamp, template version, and full selection manifest to metadata.json

**Checkpoint**: User Story 3 complete - developers can understand their stack and plan migrations

---

## Phase 6: User Story 4 - Deploy to Production (Priority: P2)

**Goal**: Enable one-command deployment to production with all services connected and working

**Independent Test**: Generate application, run deployment command, verify production deployment successful with working auth, billing, and data persistence

### Database Migration Templates (US4)

- [ ] T081 [P] [US4] Create Prisma migration scripts in template/files/node/saas/integrations/orm/prisma/migrations/ for initial schema
- [ ] T082 [P] [US4] Create Drizzle migration scripts in template/files/node/saas/integrations/orm/drizzle/migrations/ for initial schema
- [ ] T083 [US4] Add migration validation to CI workflows in template/files/shared/.github/workflows/saas-deploy.yml.jinja

### Deployment Scripts (US4)

- [ ] T084 [P] [US4] Create Vercel deployment script in template/files/node/saas/hosting/vercel/deploy.sh.jinja
- [ ] T085 [P] [US4] Create Cloudflare deployment script in template/files/node/saas/hosting/cloudflare/deploy.sh.jinja
- [ ] T086 [US4] Add pre-deployment checks script in template/files/shared/saas-starter/scripts/pre-deploy.sh.jinja validating environment variables

### Health Check Endpoints (US4)

- [ ] T087 [P] [US4] Create Next.js health check endpoint in template/files/node/saas/runtime/nextjs/app/api/health/route.ts.jinja
- [ ] T088 [P] [US4] Create Remix health check endpoint in template/files/node/saas/runtime/remix/app/routes/api.health.ts.jinja
- [ ] T089 [US4] Implement service connectivity checks in health endpoints (database, auth provider, billing provider)

### Production Configuration (US4)

- [ ] T090 [US4] Add production environment variable configuration to deployment workflows
- [ ] T091 [US4] Create production-specific Next.js config in next.config.js.jinja (logging, performance, security)
- [ ] T092 [US4] Create production-specific Remix config in remix.config.js.jinja

### Webhook Configuration (US4)

- [ ] T093 [P] [US4] Create Stripe webhook handler in template/files/node/saas/integrations/billing/stripe/webhooks.ts.jinja
- [ ] T094 [P] [US4] Create Clerk webhook handler in template/files/node/saas/integrations/auth/clerk/webhooks.ts.jinja
- [ ] T095 [US4] Add webhook verification and signature validation to all webhook handlers

### Monitoring Setup (US4)

- [ ] T096 [US4] Configure Sentry production DSN and environment in observability templates
- [ ] T097 [US4] Configure Datadog production API keys and environment in observability templates
- [ ] T098 [US4] Add deployment tracking to observability integrations (Sentry releases, Datadog deployment markers)

**Checkpoint**: User Story 4 complete - applications deploy to production successfully

---

## Phase 7: Seeded Fixtures & Test Data (Cross-Cutting)

**Purpose**: Generate realistic development data

- [ ] T099 [P] Create Prisma seed script in template/files/node/saas/fixtures/seed.prisma.ts.jinja with example users, organizations, subscriptions from data-model.md
- [ ] T100 [P] Create Drizzle seed script in template/files/node/saas/fixtures/seed.drizzle.ts.jinja with same entities
- [ ] T101 [P] Create Faker.js factory pattern in template/files/node/saas/factories/index.ts.jinja for test data generation
- [ ] T102 Create fixture user data in template/files/node/saas/fixtures/users.ts.jinja with 10 deterministic users (IDs 1-10)
- [ ] T103 [P] Create fixture organization data in template/files/node/saas/fixtures/organizations.ts.jinja with 5 organizations
- [ ] T104 [P] Create fixture subscription data in template/files/node/saas/fixtures/subscriptions.ts.jinja with various plan types
- [ ] T105 Add pnpm db:seed command to package.json.jinja scripts

---

## Phase 8: Enterprise Features (WorkOS Integration)

**Purpose**: Add optional enterprise authentication capabilities

- [ ] T106 [P] Create WorkOS integration in template/files/node/saas/integrations/enterprise/workos/client.ts.jinja
- [ ] T107 [P] Create WorkOS SSO configuration in template/files/node/saas/integrations/enterprise/workos/sso.ts.jinja
- [ ] T108 [P] Create WorkOS Directory Sync (SCIM) configuration in template/files/node/saas/integrations/enterprise/workos/scim.ts.jinja
- [ ] T109 Create WorkOS webhook handlers in template/files/node/saas/integrations/enterprise/workos/webhooks.ts.jinja
- [ ] T110 Add WorkOS integration to auth middleware when enterprise_bridge=workos

---

## Phase 9: Sample Renders & Testing

**Purpose**: Validate all 26 technology combinations work correctly

- [ ] T111 Create sample render for Vercel Starter stack in samples/saas-starter/nextjs-vercel-neon-clerk/copier-answers.yml
- [ ] T112 Create sample render for Edge Optimized stack in samples/saas-starter/remix-cloudflare-neon-authjs/copier-answers.yml
- [ ] T113 Create sample render for All-in-One Platform stack in samples/saas-starter/nextjs-vercel-supabase-clerk/copier-answers.yml
- [ ] T114 Create sample render for Enterprise Ready stack in samples/saas-starter/nextjs-vercel-neon-clerk-workos/copier-answers.yml
- [ ] T115 Implement validate_saas_combinations.py to render and smoke test all 26 valid combinations (smoke test passes when: application renders without errors, health checks pass, environment validation succeeds, post-gen hook completes successfully)
- [ ] T116 Add SaaS starter validation to CI workflow in .github/workflows/saas-validation.yml
- [ ] T117 Generate smoke results metadata in samples/saas-starter/metadata.json with success rates per combination

---

## Phase 10: Documentation & Polish

**Purpose**: Complete documentation for template users and generated application developers

- [ ] T118 [P] Copy quickstart.md content to template/files/shared/docs/saas-starter-quickstart.md.jinja
- [ ] T119 [P] Create troubleshooting guide in template/files/shared/docs/saas-starter-troubleshooting.md.jinja
- [ ] T120 [P] Create deployment guide in template/files/shared/docs/saas-starter-deployment.md.jinja
- [ ] T121 [P] Create security guide in template/files/shared/docs/saas-starter-security.md.jinja
- [ ] T122 Create 28 integration-specific docs (docs/integrations/{service}.md.jinja) covering setup, API usage, troubleshooting, and external links for each service (Clerk, Auth.js, Stripe, Paddle, Trigger.dev, Inngest, Resend, Postmark, PostHog, Amplitude, OpenAI, Anthropic, R2, Supabase Storage, Neon, Supabase, Prisma, Drizzle, Next.js, Remix, Vercel, Cloudflare, GitHub Actions, Cloudflare CI, Sentry, Datadog, OpenTelemetry, WorkOS)
- [ ] T123 Update main Riso README.md to include SaaS starter module documentation
- [ ] T124 Update AGENTS.md to include SaaS starter in Active Technologies section
- [ ] T125 Create module catalog entry in template/files/shared/module_catalog.json.jinja for saas-starter
- [ ] T126 Run validate_dockerfiles.py and validate_workflows.py on generated SaaS samples
- [ ] T127 Update .github/copilot-instructions.md with SaaS starter technologies (already complete)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - Core functionality, must complete first
- **User Story 2 (Phase 4)**: Can start after Foundational (Phase 2) - Independent from US1 implementation
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) - Uses config infrastructure from Phase 2
- **User Story 4 (Phase 6)**: Depends on User Story 1 (Phase 3) - Requires deployable applications from US1
- **Fixtures (Phase 7)**: Depends on User Story 1 (Phase 3) - Requires database schemas from US1
- **Enterprise (Phase 8)**: Depends on User Story 1 (Phase 3) - Requires auth infrastructure from US1
- **Sample Renders (Phase 9)**: Depends on all integration templates from Phase 3
- **Documentation (Phase 10)**: Can start in parallel with later phases, depends on feature completion

### User Story Dependencies

- **User Story 1 (P1) - Generate Stack**: FOUNDATIONAL - All other stories depend on this
- **User Story 2 (P2) - Trade-off Guidance**: Independent of US1 implementation (only depends on Foundational)
- **User Story 3 (P3) - Configuration**: Independent of US1 but uses infrastructure from Phase 2
- **User Story 4 (P2) - Deploy**: Depends on US1 (needs working applications to deploy)

### Critical Path

```
Setup (Phase 1)
  ↓
Foundational (Phase 2) ← BLOCKS everything
  ↓
User Story 1 (Phase 3) ← CRITICAL - Core template generation
  ↓
├─→ User Story 4 (Phase 6) - Deployment (depends on US1)
├─→ Fixtures (Phase 7) - Test data (depends on US1)
├─→ Enterprise (Phase 8) - WorkOS (depends on US1)
└─→ Sample Renders (Phase 9) - Validation (depends on US1)

In parallel after Foundational:
  - User Story 2 (Phase 4) - Guidance docs
  - User Story 3 (Phase 5) - Configuration
```

### Parallel Opportunities

**After Foundational Phase completes:**

- All runtime framework templates (T015-T020) can be developed in parallel
- All database schema templates (T021-T023) can be developed in parallel
- All auth integration templates (T024-T026) can be developed in parallel
- All billing integration templates (T027-T029) can be developed in parallel
- All background job templates (T030-T032) can be developed in parallel
- All email integration templates (T033-T036) can be developed in parallel
- All analytics templates (T037-T039) can be developed in parallel
- All AI integration templates (T040-T042) can be developed in parallel
- All storage templates (T043-T045) can be developed in parallel
- All observability templates (T046-T049) can be developed in parallel
- All hosting config templates (T050-T051) can be developed in parallel
- All CI/CD templates (T052-T053) can be developed in parallel

**User Story 2 comparison docs (T060-T070)** can all be written in parallel after Foundational phase

**After User Story 1 completes:**

- Fixtures (T099-T105) can all be developed in parallel
- Enterprise features (T106-T110) can be developed in parallel
- Sample renders (T111-T114) can be developed in parallel
- Documentation tasks (T118-T126) can be developed in parallel

---

## Parallel Example: User Story 1 Integration Templates

```bash
# All integration templates within US1 can launch together once Foundational is complete:

# Runtime frameworks
Task T015: Create Next.js base template
Task T018: Create Remix base template

# Database
Task T021: Create Prisma schema
Task T022: Create Drizzle schema

# Auth providers
Task T024: Create Clerk integration
Task T025: Create Auth.js integration

# Billing providers
Task T027: Create Stripe integration
Task T028: Create Paddle integration

# ... all integration categories proceed in parallel
```

---

## Implementation Strategy

### MVP First (Recommended Stacks Only)

1. **Complete Phase 1 + 2** (Setup + Foundational) → ~2 days
2. **Complete Phase 3** (User Story 1 - Core generation) → ~10 days
   - Focus on: Next.js, Vercel, Neon, Prisma, Clerk, Stripe, Trigger.dev, Resend, PostHog, OpenAI, R2, GitHub Actions, Sentry+Datadog
   - This is the "Vercel Starter" stack (FR-029 first option in each category)
3. **Complete Phase 6** (User Story 4 - Deployment) → ~2 days
4. **STOP and VALIDATE**: Render Vercel Starter stack, deploy to production, verify all integrations
5. **MVP COMPLETE**: Template can generate one production-ready SaaS stack

**Total MVP Timeline**: ~14 days with parallel work

### Incremental Delivery (Add Alternative Options)

After MVP:

1. **Add Remix option** (T018-T020, T088) → +1 day
2. **Add Cloudflare option** (T051, T085, T092) → +1 day
3. **Add Auth.js option** (T025, T094) → +1 day
4. **Add Paddle option** (T028, T093) → +1 day
5. Continue adding alternatives for remaining categories → +5 days
6. **Complete all 28 integrations** → Total ~22 days

Then add:

7. **Phase 4** (User Story 2 - Guidance) → +2 days
8. **Phase 5** (User Story 3 - Config docs) → +1 day
9. **Phase 7** (Fixtures) → +1 day
10. **Phase 8** (Enterprise/WorkOS) → +2 days
11. **Phase 9** (Sample renders & validation) → +2 days
12. **Phase 10** (Documentation polish) → +3 days

**Total Feature Complete Timeline**: ~33 days with parallel work

### Parallel Team Strategy

With 3 developers working simultaneously after Foundational phase:

- **Developer A**: Runtime + Hosting + CI/CD (T015-T020, T050-T053)
- **Developer B**: Database + Auth + Billing (T021-T029)
- **Developer C**: Jobs + Email + Analytics (T030-T039)

Then rotate for next batch:

- **Developer A**: AI + Storage (T040-T045)
- **Developer B**: Observability (T046-T049)
- **Developer C**: Environment + Package config (T054-T057)

This parallel approach reduces Phase 3 from ~10 days to ~4 days.

**Optimized Timeline with 3 developers**: ~20 days to feature complete

---

## Task Count Summary

- **Setup (Phase 1)**: 7 tasks
- **Foundational (Phase 2)**: 7 tasks (BLOCKING)
- **User Story 1 (Phase 3)**: 43 tasks (CRITICAL PATH)
- **User Story 2 (Phase 4)**: 15 tasks
- **User Story 3 (Phase 5)**: 8 tasks
- **User Story 4 (Phase 6)**: 15 tasks
- **Fixtures (Phase 7)**: 7 tasks
- **Enterprise (Phase 8)**: 5 tasks
- **Sample Renders (Phase 9)**: 7 tasks
- **Documentation (Phase 10)**: 10 tasks

**Total Tasks**: 127 tasks

**Parallel Tasks**: 78 tasks marked with [P] (61% of total)

**MVP Tasks (Phases 1-3, 6)**: 72 tasks (57% of total)

---

## Success Criteria Mapping

Tasks mapped to success criteria from spec.md:

- **SC-001** (render in <5min): T001-T057 (all template generation)
- **SC-002** (starts in <2min): T054-T055 (env validation), T081-T083 (migrations)
- **SC-003** (13 categories, 2 options): T004 (copier prompts), T058 (guidance)
- **SC-004** (health checks pass): T087-T089 (health endpoints)
- **SC-005** (deploy in <10min): T084-T092 (deployment scripts)
- **SC-006** (26 combinations work): T115-T117 (validation suite)
- **SC-007** (auth flow works): T024-T026 (auth integrations)
- **SC-008** (billing flow works): T027-T029 (billing integrations)
- **SC-009** (service examples work): T030-T045 (all service integrations)
- **SC-010** (documentation complete): T118-T122 (docs)
- **SC-011** (90% setup success): T009 (post-gen hook), T054 (env validation)
- **SC-012** (95% deploy success): T084-T098 (deployment + monitoring)
- **SC-013** (quality checks pass): T126 (validate scripts)
- **SC-014** (config accurate): T073-T075 (config generation)
- **SC-015** (env validation 100%): T054-T055 (env.ts validation)
- **SC-016** (CI/CD works): T052-T053 (workflow templates)
- **SC-017** (50% time reduction): All tasks collectively
- **SC-018** (OTel correlation): T048-T049 (OTel + logging)
- **SC-019** (observability in 5min): T046-T049, T096-T098 (observability setup)
- **SC-020** (5+ fixture entities): T099-T104 (fixtures)
- **SC-021** (1000+ records <10s): T101 (factory pattern)
- **SC-022** (migrations validate): T081-T083 (migration validation)
- **SC-023** (rollback <2min): T081-T083 (migration scripts)
- **SC-024** (70% coverage): Tests not included per spec
- **SC-025** (E2E <3min): Tests not included per spec

---

## Notes

- **Tests omitted**: Feature specification does not explicitly request TDD approach, so test tasks are excluded per template instructions
- **[P] marking strategy**: Tasks marked [P] work on different files with no sequential dependencies
- **Story labels**: All tasks in Phases 3-6 include [US1], [US2], [US3], or [US4] labels for traceability
- **File paths**: All paths are relative to Riso template repository root (`/workspaces/riso/`)
- **Jinja2 templates**: All generated files use `.jinja` extension for Copier processing
- **Checkpoint validation**: After completing each user story phase, verify the story is independently functional before proceeding
- **28 integrations**: User Story 1 implements all 28 service integrations (14 categories × 2 options each)
- **Constitution compliance**: Feature has justified complexity violations documented in plan.md
- **Sample combinations**: 4 recommended stacks + comprehensive validation of all 26 valid combinations (some invalid per compatibility rules)
