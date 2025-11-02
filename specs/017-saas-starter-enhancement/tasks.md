# Tasks: SaaS Starter Comprehensive Enhancement

**Input**: Design documents from `/workspaces/riso/specs/017-saas-starter-enhancement/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are EXCLUDED per template guidance.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6, US7)
- Include exact file paths in descriptions

## Path Conventions

- Template files: `template/files/`
- Python scripts: `scripts/`, `cli/`
- Config builder: `config-builder/`
- Documentation: `docs/modules/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and foundational structure for the enhancement

- [ ] T001 Create enhanced copier.yml structure in template/copier.yml with new category sections
- [ ] T002 Update validation hooks in template/hooks/pre_gen_project.py for expanded options
- [ ] T003 [P] Create compatibility validation module in scripts/saas/compatibility_matrix.py
- [ ] T004 [P] Initialize config builder project structure in config-builder/ with Next.js 16
- [ ] T005 [P] Initialize migration tool CLI in cli/commands/migrate/ with TypeScript
- [ ] T006 [P] Create shared integration template structure in template/files/node/saas/integrations/
- [ ] T007 [P] Create multi-tenant template structure in template/files/node/saas/multi-tenant/
- [ ] T008 [P] Create dev tools structure in template/files/node/saas/dev-tools/
- [ ] T009 Update sample configurations in samples/saas-starter/ with new options
- [ ] T010 [P] Create enhanced documentation templates in docs/modules/saas-starter-enhanced.md.jinja

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Implement copier prompt definitions for all 21 categories in template/copier.yml
- [ ] T012 [P] Create validation logic for 100+ technology combinations in scripts/saas/compatibility_matrix.py
- [ ] T013 [P] Implement base integration template patterns in template/files/shared/saas/base_integration.ts.jinja
- [ ] T014 [P] Create environment variable validation framework in template/files/shared/saas/env_validation.ts.jinja
- [ ] T015 [P] Implement cost estimation calculator in scripts/saas/cost_calculator.py
- [ ] T016 [P] Create architecture diagram generator in scripts/saas/diagram_generator.py
- [ ] T017 Setup CI validation for all combinations in scripts/ci/validate_saas_combinations.py
- [ ] T018 [P] Create sample render script in scripts/ci/render_saas_samples.py
- [ ] T019 Create metadata tracking for all integrations in template/files/shared/saas/metadata.json.jinja
- [ ] T020 Implement copier answers export/import in scripts/saas/config_manager.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Select from Expanded Technology Options (Priority: P1) 🎯 MVP

**Goal**: Expand original 14 categories from 2 to 4 options each with clear use-when guidance

**Independent Test**: Run Copier with expanded options, select any combination from 56 integrations (14 × 4), verify generated application works with proper integration initialization and error handling

### Implementation for User Story 1

#### Database Expansion (4 options)

- [ ] T021 [P] [US1] Create Neon integration template in template/files/node/saas/integrations/database/neon/
- [ ] T022 [P] [US1] Create Supabase integration template in template/files/node/saas/integrations/database/supabase/
- [ ] T023 [P] [US1] Create PlanetScale integration template in template/files/node/saas/integrations/database/planetscale/
- [ ] T024 [P] [US1] Create CockroachDB integration template in template/files/node/saas/integrations/database/cockroachdb/

#### Runtime Expansion (4 options)

- [ ] T025 [P] [US1] Create Next.js 16 runtime template in template/files/node/saas/runtime/nextjs/
- [ ] T026 [P] [US1] Create Remix 2.x runtime template in template/files/node/saas/runtime/remix/
- [ ] T027 [P] [US1] Create SvelteKit 2.x runtime template in template/files/node/saas/runtime/sveltekit/
- [ ] T028 [P] [US1] Create Astro 4.x runtime template in template/files/node/saas/runtime/astro/

#### Hosting Expansion (4 options)

- [ ] T029 [P] [US1] Create Vercel hosting config in template/files/node/saas/hosting/vercel/
- [ ] T030 [P] [US1] Create Cloudflare hosting config in template/files/node/saas/hosting/cloudflare/
- [ ] T031 [P] [US1] Create Netlify hosting config in template/files/node/saas/hosting/netlify/
- [ ] T032 [P] [US1] Create Railway hosting config in template/files/node/saas/hosting/railway/

#### ORM Expansion (4 options)

- [ ] T033 [P] [US1] Create Prisma ORM templates in template/files/node/saas/integrations/orm/prisma/
- [ ] T034 [P] [US1] Create Drizzle ORM templates in template/files/node/saas/integrations/orm/drizzle/
- [ ] T035 [P] [US1] Create Kysely query builder templates in template/files/node/saas/integrations/orm/kysely/
- [ ] T036 [P] [US1] Create TypeORM templates in template/files/node/saas/integrations/orm/typeorm/

#### Auth Expansion (4 options)

- [ ] T037 [P] [US1] Create Clerk auth integration in template/files/node/saas/integrations/auth/clerk/
- [ ] T038 [P] [US1] Create Auth.js v5 integration in template/files/node/saas/integrations/auth/authjs/
- [ ] T039 [P] [US1] Create WorkOS auth integration in template/files/node/saas/integrations/auth/workos/
- [ ] T040 [P] [US1] Create Supabase Auth integration in template/files/node/saas/integrations/auth/supabase-auth/

#### Storage Expansion (4 options)

- [ ] T041 [P] [US1] Create Cloudflare R2 storage integration in template/files/node/saas/integrations/storage/r2/
- [ ] T042 [P] [US1] Create Supabase Storage integration in template/files/node/saas/integrations/storage/supabase-storage/
- [ ] T043 [P] [US1] Create AWS S3 storage integration in template/files/node/saas/integrations/storage/aws-s3/
- [ ] T044 [P] [US1] Create UploadThing integration in template/files/node/saas/integrations/storage/uploadthing/

#### Email Expansion (4 options)

- [ ] T045 [P] [US1] Create Resend + React Email integration in template/files/node/saas/integrations/email/resend/
- [ ] T046 [P] [US1] Create Postmark integration in template/files/node/saas/integrations/email/postmark/
- [ ] T047 [P] [US1] Create SendGrid integration in template/files/node/saas/integrations/email/sendgrid/
- [ ] T048 [P] [US1] Create AWS SES integration in template/files/node/saas/integrations/email/aws-ses/

#### AI Expansion (4 options)

- [ ] T049 [P] [US1] Create OpenAI GPT integration in template/files/node/saas/integrations/ai/openai/
- [ ] T050 [P] [US1] Create Anthropic Claude integration in template/files/node/saas/integrations/ai/anthropic/
- [ ] T051 [P] [US1] Create Google Gemini integration in template/files/node/saas/integrations/ai/gemini/
- [ ] T052 [P] [US1] Create Ollama local LLM integration in template/files/node/saas/integrations/ai/ollama/

#### Integration Testing & Validation

- [ ] T053 [US1] Update copier prompts with all expanded options in template/copier.yml
- [ ] T054 [US1] Add use-when guidance for all 56 integrations in contracts/copier-prompts.yml
- [ ] T055 [US1] Update compatibility validation for expanded combinations in scripts/saas/compatibility_matrix.py
- [ ] T056 [US1] Create quickstart examples for each new integration in docs/modules/integration-guides/
- [ ] T057 [US1] Generate sample renders for expanded options in samples/saas-starter/expanded-options/
- [ ] T058 [US1] Run validation suite for all 56 integrations via scripts/ci/validate_saas_combinations.py

**Checkpoint**: At this point, User Story 1 should be fully functional - developers can select from 4 options per original category and generate working applications

---

## Phase 4: User Story 2 - Configure Additional Infrastructure Categories (Priority: P1)

**Goal**: Add 7 new infrastructure categories (search, cache, feature flags, CMS, usage metering, secrets, error tracking) with 3-4 options each

**Independent Test**: Enable each new category independently, verify proper integration with existing categories (database, auth, hosting), confirm working examples in generated application

### Implementation for User Story 2

#### Search Category (3 options)

- [ ] T059 [P] [US2] Create Algolia search integration in template/files/node/saas/integrations/search/algolia/
- [ ] T060 [P] [US2] Create Meilisearch integration in template/files/node/saas/integrations/search/meilisearch/
- [ ] T061 [P] [US2] Create Typesense integration in template/files/node/saas/integrations/search/typesense/
- [ ] T062 [US2] Add search synchronization patterns with database integrations in template/files/node/saas/integrations/search/sync-patterns.ts.jinja
- [ ] T063 [US2] Create search indexing examples in template/files/node/saas/examples/search/

#### Cache Category (3 options)

- [ ] T064 [P] [US2] Create Redis via Upstash integration in template/files/node/saas/integrations/cache/redis/
- [ ] T065 [P] [US2] Create Cloudflare KV integration in template/files/node/saas/integrations/cache/cloudflare-kv/
- [ ] T066 [P] [US2] Create Vercel KV integration in template/files/node/saas/integrations/cache/vercel-kv/
- [ ] T067 [US2] Add cache invalidation patterns in template/files/node/saas/integrations/cache/invalidation-patterns.ts.jinja
- [ ] T068 [US2] Create cache warming examples in template/files/node/saas/examples/cache/

#### Feature Flags Category (3 options)

- [ ] T069 [P] [US2] Create LaunchDarkly integration in template/files/node/saas/integrations/feature-flags/launchdarkly/
- [ ] T070 [P] [US2] Create PostHog feature flags integration in template/files/node/saas/integrations/feature-flags/posthog/
- [ ] T071 [P] [US2] Create GrowthBook integration in template/files/node/saas/integrations/feature-flags/growthbook/
- [ ] T072 [US2] Add feature flag evaluation patterns with auth provider in template/files/node/saas/integrations/feature-flags/auth-integration.ts.jinja
- [ ] T073 [US2] Create feature flag rollout examples in template/files/node/saas/examples/feature-flags/

#### CMS Category (4 options)

- [ ] T074 [P] [US2] Create Contentful integration in template/files/node/saas/integrations/cms/contentful/
- [ ] T075 [P] [US2] Create Sanity integration in template/files/node/saas/integrations/cms/sanity/
- [ ] T076 [P] [US2] Create Payload CMS integration in template/files/node/saas/integrations/cms/payload/
- [ ] T077 [P] [US2] Create Strapi integration in template/files/node/saas/integrations/cms/strapi/
- [ ] T078 [US2] Add CMS content delivery patterns with frontend framework in template/files/node/saas/integrations/cms/delivery-patterns.ts.jinja
- [ ] T079 [US2] Create CMS admin panel examples in template/files/node/saas/examples/cms/

#### Usage Metering Category (3 options)

- [ ] T080 [P] [US2] Create Stripe Metering integration in template/files/node/saas/integrations/usage-metering/stripe-metering/
- [ ] T081 [P] [US2] Create Moesif integration in template/files/node/saas/integrations/usage-metering/moesif/
- [ ] T082 [P] [US2] Create Amberflo integration in template/files/node/saas/integrations/usage-metering/amberflo/
- [ ] T083 [US2] Add usage tracking patterns with billing provider in template/files/node/saas/integrations/usage-metering/billing-integration.ts.jinja
- [ ] T084 [US2] Create usage aggregation examples in template/files/node/saas/examples/usage-metering/

#### Secrets Management Category (4 options)

- [ ] T085 [P] [US2] Create Infisical integration in template/files/node/saas/integrations/secrets/infisical/
- [ ] T086 [P] [US2] Create Doppler integration in template/files/node/saas/integrations/secrets/doppler/
- [ ] T087 [P] [US2] Create AWS Secrets Manager integration in template/files/node/saas/integrations/secrets/aws-secrets/
- [ ] T088 [P] [US2] Create environment file patterns in template/files/node/saas/integrations/secrets/env-files/
- [ ] T089 [US2] Add secrets rotation procedures in template/files/node/saas/integrations/secrets/rotation-guide.md.jinja
- [ ] T090 [US2] Create secrets validation examples in template/files/node/saas/examples/secrets/

#### Enhanced Error Tracking Category (3 options)

- [ ] T091 [P] [US2] Create enhanced Sentry integration in template/files/node/saas/integrations/error-tracking/sentry/
- [ ] T092 [P] [US2] Create Rollbar integration in template/files/node/saas/integrations/error-tracking/rollbar/
- [ ] T093 [P] [US2] Create BugSnag integration in template/files/node/saas/integrations/error-tracking/bugsnag/
- [ ] T094 [US2] Add error grouping patterns in template/files/node/saas/integrations/error-tracking/grouping-patterns.ts.jinja
- [ ] T095 [US2] Create error monitoring dashboards in template/files/node/saas/examples/error-tracking/

#### Category Integration & Validation

- [ ] T096 [US2] Add all 7 new categories to copier prompts in template/copier.yml
- [ ] T097 [US2] Update compatibility validation for new category interactions in scripts/saas/compatibility_matrix.py
- [ ] T098 [US2] Create cross-category integration patterns in docs/modules/integration-patterns.md.jinja
- [ ] T099 [US2] Generate sample renders with new categories in samples/saas-starter/new-categories/
- [ ] T100 [US2] Run validation suite for 80+ total integrations via scripts/ci/validate_saas_combinations.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - developers can select from 21 total categories with 80+ integrations

---

## Phase 5: User Story 3 - Use Visual Configuration Builder (Priority: P2)

**Goal**: Build interactive web UI and CLI TUI for exploring options, validating compatibility, estimating costs, generating architecture diagrams

**Independent Test**: Launch config builder, select various technologies, verify validation works, export copier-answers.yml, use with Copier to generate matching application

### Implementation for User Story 3

#### Config Builder Web UI

- [ ] T101 [P] [US3] Initialize Next.js 16 project in config-builder/ with React 19.2
- [ ] T102 [P] [US3] Create CategoryGrid component in config-builder/components/category-grid.tsx
- [ ] T103 [P] [US3] Create OptionCard component in config-builder/components/option-card.tsx
- [ ] T104 [P] [US3] Create ValidationPanel component in config-builder/components/validation-panel.tsx
- [ ] T105 [P] [US3] Create CostEstimator component in config-builder/components/cost-estimator.tsx
- [ ] T106 [P] [US3] Create ArchitectureDiagram component in config-builder/components/architecture-diagram.tsx
- [ ] T107 [P] [US3] Create ConfigComparison component in config-builder/components/config-comparison.tsx
- [ ] T108 [US3] Implement main configuration page in config-builder/app/page.tsx
- [ ] T109 [US3] Create configuration state management in config-builder/lib/config-store.ts

#### Config Builder API Routes

- [ ] T110 [P] [US3] Create /api/options endpoint in config-builder/app/api/options/route.ts
- [ ] T111 [P] [US3] Create /api/validate endpoint in config-builder/app/api/validate/route.ts
- [ ] T112 [P] [US3] Create /api/estimate endpoint in config-builder/app/api/estimate/route.ts
- [ ] T113 [P] [US3] Create /api/diagram endpoint in config-builder/app/api/diagram/route.ts
- [ ] T114 [P] [US3] Create /api/export endpoint in config-builder/app/api/export/route.ts
- [ ] T115 [P] [US3] Create /api/import endpoint in config-builder/app/api/import/route.ts
- [ ] T116 [US3] Implement real-time validation logic in config-builder/lib/validator.ts
- [ ] T117 [US3] Implement cost calculation engine in config-builder/lib/cost-calculator.ts

#### CLI TUI (Terminal UI)

- [ ] T118 [P] [US3] Initialize Ink-based TUI in config-builder/cli/tui.tsx
- [ ] T119 [P] [US3] Create TUI category selection screen in config-builder/cli/screens/category-selection.tsx
- [ ] T120 [P] [US3] Create TUI option details screen in config-builder/cli/screens/option-details.tsx
- [ ] T121 [P] [US3] Create TUI validation screen in config-builder/cli/screens/validation.tsx
- [ ] T122 [P] [US3] Create TUI cost estimator screen in config-builder/cli/screens/cost-estimator.tsx
- [ ] T123 [P] [US3] Create TUI export screen in config-builder/cli/screens/export.tsx
- [ ] T124 [US3] Implement TUI navigation logic in config-builder/cli/navigation.ts
- [ ] T125 [US3] Create CLI command entry point in config-builder/cli/index.ts

#### Export/Import & Persistence

- [ ] T126 [P] [US3] Implement YAML export logic in config-builder/lib/exporters/yaml-exporter.ts
- [ ] T127 [P] [US3] Implement JSON export logic in config-builder/lib/exporters/json-exporter.ts
- [ ] T128 [P] [US3] Implement configuration import logic in config-builder/lib/importers/config-importer.ts
- [ ] T129 [P] [US3] Create localStorage persistence in config-builder/lib/storage/local-storage.ts
- [ ] T130 [P] [US3] Create configuration comparison logic in config-builder/lib/comparator.ts
- [ ] T131 [US3] Implement autosave functionality in config-builder/lib/autosave.ts

#### Integration & Launch

- [ ] T132 [US3] Add config builder launch script to package.json: pnpm config:builder
- [ ] T133 [US3] Create config builder documentation in docs/modules/config-builder.md.jinja
- [ ] T134 [US3] Add config builder examples in docs/modules/config-builder-examples.md.jinja
- [ ] T135 [US3] Create quickstart guide for config builder in docs/quickstart-config-builder.md.jinja
- [ ] T136 [US3] Verify exported configs work with Copier via scripts/ci/test_config_builder.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - developers can use visual/TUI config builder or manual Copier prompts

---

## Phase 6: User Story 4 - Migrate Between Technology Choices (Priority: P2)

**Goal**: Build CLI tool for post-generation technology swaps with automated code analysis, diff generation, and rollback

**Independent Test**: Generate app with one stack, run migration tool to swap specific technologies, verify application works post-migration, test rollback restores previous state

### Implementation for User Story 4

#### Migration CLI Framework

- [ ] T137 [P] [US4] Create migration command structure in cli/commands/migrate/index.ts
- [ ] T138 [P] [US4] Implement migration analysis phase in cli/commands/migrate/analyze.ts
- [ ] T139 [P] [US4] Implement migration planning phase in cli/commands/migrate/plan.ts
- [ ] T140 [P] [US4] Implement migration execution phase in cli/commands/migrate/execute.ts
- [ ] T141 [P] [US4] Implement migration validation phase in cli/commands/migrate/validate.ts
- [ ] T142 [P] [US4] Implement rollback mechanism in cli/commands/migrate/rollback.ts
- [ ] T143 [US4] Create migration progress reporter in cli/commands/migrate/progress.ts
- [ ] T144 [US4] Create migration error handler in cli/commands/migrate/error-handler.ts

#### Migration Strategies (Category-Specific)

- [ ] T145 [P] [US4] Create auth migration strategy in cli/commands/migrate/strategies/auth-migration.ts
- [ ] T146 [P] [US4] Create database migration strategy in cli/commands/migrate/strategies/database-migration.ts
- [ ] T147 [P] [US4] Create ORM migration strategy in cli/commands/migrate/strategies/orm-migration.ts
- [ ] T148 [P] [US4] Create storage migration strategy in cli/commands/migrate/strategies/storage-migration.ts
- [ ] T149 [P] [US4] Create email migration strategy in cli/commands/migrate/strategies/email-migration.ts
- [ ] T150 [P] [US4] Create search migration strategy in cli/commands/migrate/strategies/search-migration.ts
- [ ] T151 [P] [US4] Create cache migration strategy in cli/commands/migrate/strategies/cache-migration.ts
- [ ] T152 [US4] Create base migration strategy interface in cli/commands/migrate/strategies/base-strategy.ts

#### Code Analysis & Transformation

- [ ] T153 [P] [US4] Implement file scanner for technology detection in cli/commands/migrate/analysis/file-scanner.ts
- [ ] T154 [P] [US4] Implement dependency analyzer in cli/commands/migrate/analysis/dependency-analyzer.ts
- [ ] T155 [P] [US4] Implement AST-based code transformer in cli/commands/migrate/transformers/code-transformer.ts
- [ ] T156 [P] [US4] Implement import statement transformer in cli/commands/migrate/transformers/import-transformer.ts
- [ ] T157 [P] [US4] Implement configuration file transformer in cli/commands/migrate/transformers/config-transformer.ts
- [ ] T158 [P] [US4] Create diff generator in cli/commands/migrate/diff-generator.ts
- [ ] T159 [US4] Create three-way merge handler in cli/commands/migrate/merge-handler.ts

#### Database Migration Handling

- [ ] T160 [P] [US4] Implement PostgreSQL schema export in cli/commands/migrate/database/postgres-export.ts
- [ ] T161 [P] [US4] Implement MySQL schema export in cli/commands/migrate/database/mysql-export.ts
- [ ] T162 [P] [US4] Implement schema compatibility checker in cli/commands/migrate/database/schema-compat.ts
- [ ] T163 [P] [US4] Implement data migration scripts in cli/commands/migrate/database/data-migration.ts
- [ ] T164 [US4] Create database backup handler in cli/commands/migrate/database/backup-handler.ts

#### Test Suite Updates

- [ ] T165 [P] [US4] Implement test file transformer in cli/commands/migrate/transformers/test-transformer.ts
- [ ] T166 [P] [US4] Create test validation runner in cli/commands/migrate/validation/test-runner.ts
- [ ] T167 [US4] Create post-migration test reporter in cli/commands/migrate/validation/test-reporter.ts

#### Integration & Documentation

- [ ] T168 [US4] Add migration command to CLI entry point in cli/index.ts
- [ ] T169 [US4] Create migration tool documentation in docs/modules/migration-tool.md.jinja
- [ ] T170 [US4] Create migration examples for each category in docs/modules/migration-examples/
- [ ] T171 [US4] Create migration troubleshooting guide in docs/modules/migration-troubleshooting.md.jinja
- [ ] T172 [US4] Verify migration tool via scripts/ci/test_migration_tool.py

**Checkpoint**: At this point, User Stories 1-4 all work independently - developers can migrate technologies post-generation with automated tooling

---

## Phase 7: User Story 5 - Deploy Multi-Tenant B2B SaaS Patterns (Priority: P2)

**Goal**: Add multi-tenant architecture patterns with 3 isolation levels (RLS, schema-per-tenant, DB-per-tenant), tenant provisioning, subdomain routing

**Independent Test**: Select multi-tenant architecture, generate app, create multiple tenants, verify data isolation (0 cross-tenant leaks), test subdomain routing and per-tenant billing

### Implementation for User Story 5

#### Row-Level Security (RLS) Pattern

- [ ] T173 [P] [US5] Create RLS middleware in template/files/node/saas/multi-tenant/rls/middleware.ts.jinja
- [ ] T174 [P] [US5] Create RLS database policies in template/files/node/saas/multi-tenant/rls/policies.sql.jinja
- [ ] T175 [P] [US5] Create tenant context setter in template/files/node/saas/multi-tenant/rls/tenant-context.ts.jinja
- [ ] T176 [P] [US5] Create RLS Prisma middleware in template/files/node/saas/multi-tenant/rls/prisma-middleware.ts.jinja
- [ ] T177 [US5] Create RLS examples in template/files/node/saas/examples/multi-tenant/rls/

#### Schema-per-Tenant Pattern

- [ ] T178 [P] [US5] Create schema provisioning logic in template/files/node/saas/multi-tenant/schema/provisioning.ts.jinja
- [ ] T179 [P] [US5] Create dynamic schema connection in template/files/node/saas/multi-tenant/schema/connection.ts.jinja
- [ ] T180 [P] [US5] Create schema migration runner in template/files/node/saas/multi-tenant/schema/migrations.ts.jinja
- [ ] T181 [US5] Create schema-per-tenant examples in template/files/node/saas/examples/multi-tenant/schema/

#### Database-per-Tenant Pattern

- [ ] T182 [P] [US5] Create database provisioning logic in template/files/node/saas/multi-tenant/database/provisioning.ts.jinja
- [ ] T183 [P] [US5] Create connection pool manager in template/files/node/saas/multi-tenant/database/connection-manager.ts.jinja
- [ ] T184 [P] [US5] Create database backup procedures in template/files/node/saas/multi-tenant/database/backup.ts.jinja
- [ ] T185 [US5] Create DB-per-tenant examples in template/files/node/saas/examples/multi-tenant/database/

#### Tenant Management

- [ ] T186 [P] [US5] Create Tenant entity model in template/files/node/saas/models/tenant.ts.jinja
- [ ] T187 [P] [US5] Create tenant provisioning API in template/files/node/saas/api/tenants/provision.ts.jinja
- [ ] T188 [P] [US5] Create tenant management API in template/files/node/saas/api/tenants/manage.ts.jinja
- [ ] T189 [P] [US5] Create tenant admin portal UI in template/files/node/saas/ui/admin/tenants/
- [ ] T190 [US5] Create tenant service in template/files/node/saas/services/tenant-service.ts.jinja

#### Subdomain Routing

- [ ] T191 [P] [US5] Create subdomain resolution middleware in template/files/node/saas/multi-tenant/routing/subdomain-middleware.ts.jinja
- [ ] T192 [P] [US5] Create DNS configuration templates in template/files/node/saas/multi-tenant/routing/dns-config.ts.jinja
- [ ] T193 [P] [US5] Create custom domain support in template/files/node/saas/multi-tenant/routing/custom-domains.ts.jinja
- [ ] T194 [US5] Create routing examples in template/files/node/saas/examples/multi-tenant/routing/

#### Per-Tenant Features

- [ ] T195 [P] [US5] Create per-tenant feature flags integration in template/files/node/saas/multi-tenant/features/feature-flags.ts.jinja
- [ ] T196 [P] [US5] Create per-tenant branding in template/files/node/saas/multi-tenant/branding/tenant-branding.ts.jinja
- [ ] T197 [P] [US5] Create per-tenant usage tracking in template/files/node/saas/multi-tenant/usage/tracking.ts.jinja
- [ ] T198 [P] [US5] Create per-tenant billing integration in template/files/node/saas/multi-tenant/billing/tenant-billing.ts.jinja
- [ ] T199 [US5] Create tenant quotas enforcement in template/files/node/saas/multi-tenant/quotas/enforcement.ts.jinja

#### Security & Isolation Testing

- [ ] T200 [P] [US5] Create tenant isolation test suite in template/files/node/saas/tests/multi-tenant/isolation.test.ts.jinja
- [ ] T201 [P] [US5] Create cross-tenant access prevention tests in template/files/node/saas/tests/multi-tenant/security.test.ts.jinja
- [ ] T202 [US5] Create tenant provisioning tests in template/files/node/saas/tests/multi-tenant/provisioning.test.ts.jinja

#### Integration & Documentation

- [ ] T203 [US5] Add multi-tenant architecture prompts to template/copier.yml
- [ ] T204 [US5] Create multi-tenant documentation in docs/modules/multi-tenant.md.jinja
- [ ] T205 [US5] Create migration guide to multi-tenant in docs/modules/multi-tenant-migration.md.jinja
- [ ] T206 [US5] Generate multi-tenant sample renders in samples/saas-starter/multi-tenant/
- [ ] T207 [US5] Verify multi-tenant isolation via scripts/ci/test_multi_tenant.py

**Checkpoint**: At this point, User Stories 1-5 all work independently - developers can deploy B2B multi-tenant SaaS with complete tenant isolation

---

## Phase 8: User Story 6 - Utilize Enhanced Local Development Tools (Priority: P3)

**Goal**: Build unified dev dashboard, one-command setup, offline mode with service mocking, fixture management, unified log aggregation

**Independent Test**: Run pnpm dev:setup to initialize all services, launch dev dashboard to view service status, enable offline mode, generate fixtures, view unified logs

### Implementation for User Story 6

#### Dev Dashboard

- [ ] T208 [P] [US6] Create dev dashboard UI in template/files/node/saas/dev-tools/dashboard/index.tsx.jinja
- [ ] T209 [P] [US6] Create ServiceStatus component in template/files/node/saas/dev-tools/dashboard/components/service-status.tsx.jinja
- [ ] T210 [P] [US6] Create health check aggregator in template/files/node/saas/dev-tools/dashboard/health-checker.ts.jinja
- [ ] T211 [P] [US6] Create service restart controls in template/files/node/saas/dev-tools/dashboard/controls.tsx.jinja
- [ ] T212 [US6] Create dashboard server in template/files/node/saas/dev-tools/dashboard/server.ts.jinja

#### One-Command Setup

- [ ] T213 [P] [US6] Create dev-setup script in template/files/node/saas/scripts/dev-setup.sh.jinja
- [ ] T214 [P] [US6] Create docker-compose configuration in template/files/node/saas/docker-compose.dev.yml.jinja
- [ ] T215 [P] [US6] Create service wait script in template/files/node/saas/scripts/wait-for-services.sh.jinja
- [ ] T216 [P] [US6] Create environment validation in template/files/node/saas/scripts/validate-env.ts.jinja
- [ ] T217 [P] [US6] Create database migration runner in template/files/node/saas/scripts/run-migrations.sh.jinja
- [ ] T218 [US6] Create fixture seeding script in template/files/node/saas/scripts/seed-fixtures.ts.jinja

#### Offline Mode & Service Mocking

- [ ] T219 [P] [US6] Create mock service registry in template/files/node/saas/dev-tools/mocks/registry.ts.jinja
- [ ] T220 [P] [US6] Create auth service mock in template/files/node/saas/dev-tools/mocks/auth-mock.ts.jinja
- [ ] T221 [P] [US6] Create billing service mock in template/files/node/saas/dev-tools/mocks/billing-mock.ts.jinja
- [ ] T222 [P] [US6] Create AI service mock in template/files/node/saas/dev-tools/mocks/ai-mock.ts.jinja
- [ ] T223 [P] [US6] Create email service mock in template/files/node/saas/dev-tools/mocks/email-mock.ts.jinja
- [ ] T224 [P] [US6] Create storage service mock in template/files/node/saas/dev-tools/mocks/storage-mock.ts.jinja
- [ ] T225 [US6] Create offline mode toggle in template/files/node/saas/dev-tools/offline-mode.ts.jinja

#### Fixture Management

- [ ] T226 [P] [US6] Create fixture factory base in template/files/node/saas/fixtures/factory-base.ts.jinja
- [ ] T227 [P] [US6] Create user fixtures in template/files/node/saas/fixtures/users.ts.jinja
- [ ] T228 [P] [US6] Create organization fixtures in template/files/node/saas/fixtures/organizations.ts.jinja
- [ ] T229 [P] [US6] Create subscription fixtures in template/files/node/saas/fixtures/subscriptions.ts.jinja
- [ ] T230 [P] [US6] Create content fixtures in template/files/node/saas/fixtures/content.ts.jinja
- [ ] T231 [US6] Create fixture reset command in template/files/node/saas/scripts/reset-fixtures.ts.jinja

#### Unified Log Aggregation

- [ ] T232 [P] [US6] Create log aggregator in template/files/node/saas/dev-tools/logging/aggregator.ts.jinja
- [ ] T233 [P] [US6] Create log formatter with colors in template/files/node/saas/dev-tools/logging/formatter.ts.jinja
- [ ] T234 [P] [US6] Create correlation ID injector in template/files/node/saas/dev-tools/logging/correlation.ts.jinja
- [ ] T235 [P] [US6] Create log viewer UI in template/files/node/saas/dev-tools/logging/viewer.tsx.jinja
- [ ] T236 [US6] Create log filtering logic in template/files/node/saas/dev-tools/logging/filters.ts.jinja

#### Integration & Documentation

- [ ] T237 [US6] Add dev tools scripts to package.json in template/files/node/saas/package.json.jinja
- [ ] T238 [US6] Create dev tools documentation in docs/modules/dev-tools.md.jinja
- [ ] T239 [US6] Create dev workflow guide in docs/modules/dev-workflow.md.jinja
- [ ] T240 [US6] Create troubleshooting guide in docs/modules/dev-troubleshooting.md.jinja
- [ ] T241 [US6] Verify dev tools via scripts/ci/test_dev_tools.py

**Checkpoint**: At this point, User Stories 1-6 all work independently - developers have enhanced local development experience with dashboard, mocks, and fixtures

---

## Phase 9: User Story 7 - Deploy with Production-Ready Patterns (Priority: P2)

**Goal**: Add multi-region deployment, blue-green strategies, database read replicas, CDN integration, DDoS protection, backup/DR procedures, compliance configs

**Independent Test**: Select production patterns, generate infrastructure configs, deploy to staging, verify failover works, test rollback procedures, confirm compliance controls

### Implementation for User Story 7

#### Multi-Region Deployment

- [ ] T242 [P] [US7] Create Terraform multi-region config in template/files/node/saas/infra/terraform/multi-region.tf.jinja
- [ ] T243 [P] [US7] Create Pulumi multi-region config in template/files/node/saas/infra/pulumi/multi-region.ts.jinja
- [ ] T244 [P] [US7] Create DNS failover configuration in template/files/node/saas/infra/dns/failover.tf.jinja
- [ ] T245 [P] [US7] Create health check definitions in template/files/node/saas/api/health/
- [ ] T246 [US7] Create region selection logic in template/files/node/saas/lib/region-selector.ts.jinja

#### Blue-Green Deployment

- [ ] T247 [P] [US7] Create blue-green deployment script in template/files/node/saas/scripts/deploy-blue-green.sh.jinja
- [ ] T248 [P] [US7] Create traffic shifting configuration in template/files/node/saas/infra/traffic/shifting.tf.jinja
- [ ] T249 [P] [US7] Create automatic rollback logic in template/files/node/saas/scripts/auto-rollback.ts.jinja
- [ ] T250 [P] [US7] Create deployment validation tests in template/files/node/saas/tests/deployment/validation.test.ts.jinja
- [ ] T251 [US7] Create deployment monitoring in template/files/node/saas/monitoring/deployment-monitor.ts.jinja

#### Database High Availability

- [ ] T252 [P] [US7] Create read replica configuration in template/files/node/saas/infra/database/read-replicas.tf.jinja
- [ ] T253 [P] [US7] Create load balancing for reads in template/files/node/saas/lib/database/read-balancer.ts.jinja
- [ ] T254 [P] [US7] Create connection pooling config in template/files/node/saas/lib/database/connection-pool.ts.jinja
- [ ] T255 [US7] Create replica health monitoring in template/files/node/saas/monitoring/replica-health.ts.jinja

#### CDN & Edge Optimization

- [ ] T256 [P] [US7] Create CDN configuration for Cloudflare in template/files/node/saas/infra/cdn/cloudflare.tf.jinja
- [ ] T257 [P] [US7] Create CDN configuration for Vercel in template/files/node/saas/infra/cdn/vercel.json.jinja
- [ ] T258 [P] [US7] Create cache invalidation logic in template/files/node/saas/lib/cdn/cache-invalidation.ts.jinja
- [ ] T259 [P] [US7] Create edge rate limiting in template/files/node/saas/infra/cdn/rate-limits.tf.jinja
- [ ] T260 [US7] Create DDoS protection config in template/files/node/saas/infra/cdn/ddos-protection.tf.jinja

#### Backup & Disaster Recovery

- [ ] T261 [P] [US7] Create automated backup script in template/files/node/saas/scripts/backup-database.sh.jinja
- [ ] T262 [P] [US7] Create backup verification in template/files/node/saas/scripts/verify-backup.ts.jinja
- [ ] T263 [P] [US7] Create restore procedures in template/files/node/saas/scripts/restore-database.sh.jinja
- [ ] T264 [P] [US7] Create disaster recovery runbook in template/files/node/saas/docs/runbooks/disaster-recovery.md.jinja
- [ ] T265 [US7] Create backup monitoring in template/files/node/saas/monitoring/backup-monitor.ts.jinja

#### Compliance Configurations

- [ ] T266 [P] [US7] Create SOC2 compliance controls in template/files/node/saas/compliance/soc2/controls.md.jinja
- [ ] T267 [P] [US7] Create HIPAA compliance config in template/files/node/saas/compliance/hipaa/configuration.ts.jinja
- [ ] T268 [P] [US7] Create GDPR data handling in template/files/node/saas/compliance/gdpr/data-handling.ts.jinja
- [ ] T269 [P] [US7] Create audit logging in template/files/node/saas/lib/audit/audit-logger.ts.jinja
- [ ] T270 [P] [US7] Create data retention policies in template/files/node/saas/lib/compliance/retention.ts.jinja
- [ ] T271 [US7] Create compliance reporting in template/files/node/saas/lib/compliance/reporting.ts.jinja

#### Monitoring & Observability

- [ ] T272 [P] [US7] Create custom monitoring dashboards in template/files/node/saas/monitoring/dashboards/
- [ ] T273 [P] [US7] Create SaaS KPI metrics in template/files/node/saas/monitoring/metrics/saas-kpis.ts.jinja
- [ ] T274 [P] [US7] Create anomaly detection in template/files/node/saas/monitoring/anomaly-detection.ts.jinja
- [ ] T275 [P] [US7] Create alerting rules in template/files/node/saas/monitoring/alerts/rules.yml.jinja
- [ ] T276 [US7] Create incident response playbooks in template/files/node/saas/docs/runbooks/incident-response.md.jinja

#### Integration & Documentation

- [ ] T277 [US7] Add deployment pattern prompts to template/copier.yml
- [ ] T278 [US7] Create production deployment guide in docs/modules/production-deployment.md.jinja
- [ ] T279 [US7] Create infrastructure documentation in docs/modules/infrastructure.md.jinja
- [ ] T280 [US7] Create runbooks for operations in docs/runbooks/
- [ ] T281 [US7] Generate production-ready samples in samples/saas-starter/production/
- [ ] T282 [US7] Verify production patterns via scripts/ci/test_production_patterns.py

**Checkpoint**: All user stories (1-7) now work independently - full enterprise-grade SaaS starter with production patterns complete

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, documentation, validation, optimization

- [ ] T283 [P] Update main SaaS starter documentation in docs/modules/saas-starter-enhanced.md.jinja
- [ ] T284 [P] Create comprehensive upgrade guide from 012-saas-starter in docs/upgrade-guide/012-to-017.md.jinja
- [ ] T285 [P] Create architecture decision records in docs/architecture/decisions/
- [ ] T286 [P] Update sample configurations for all patterns in samples/saas-starter/
- [ ] T287 [P] Create cost optimization guide in docs/guides/cost-optimization.md.jinja
- [ ] T288 [P] Create security hardening guide in docs/guides/security-hardening.md.jinja
- [ ] T289 [P] Create performance tuning guide in docs/guides/performance-tuning.md.jinja
- [ ] T290 [P] Update AGENTS.md with new feature details
- [ ] T291 [P] Update .github/copilot-instructions.md with enhanced SaaS starter info
- [ ] T292 Code cleanup and refactoring across all templates
- [ ] T293 Performance optimization for template rendering (target <7 minutes)
- [ ] T294 Run comprehensive validation suite via scripts/ci/validate_all.py
- [ ] T295 Generate all sample renders via scripts/render-samples.sh
- [ ] T296 Run quickstart.md validation for all user stories
- [ ] T297 Update feature metadata in specs/017-saas-starter-enhancement/metadata.json
- [ ] T298 Final constitution check verification
- [ ] T299 Create release notes and changelog entry
- [ ] T300 Submit PR with comprehensive test evidence and documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Core expansion, can proceed first
- **User Story 2 (Phase 4)**: Depends on Foundational - New categories, can proceed after/parallel with US1
- **User Story 3 (Phase 5)**: Depends on Foundational + US1 + US2 data (needs all options to display)
- **User Story 4 (Phase 6)**: Depends on Foundational + US1 + US2 (needs all integrations to migrate between)
- **User Story 5 (Phase 7)**: Depends on Foundational (independent architecture pattern)
- **User Story 6 (Phase 8)**: Depends on Foundational + US1 + US2 (needs integrations for dashboard/mocks)
- **User Story 7 (Phase 9)**: Depends on Foundational (independent deployment patterns)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

**Critical Path** (must complete in order):
1. **Foundational (Phase 2)** → Blocks everything
2. **User Story 1 (P1)** → Expanded options (needed by US3, US4)
3. **User Story 2 (P1)** → New categories (needed by US3, US4)
4. **User Story 3 (P2)** → Config builder (depends on US1+US2 data)
5. **User Story 4 (P2)** → Migration tool (depends on US1+US2 integrations)

**Independent** (can work in parallel after Foundational):
- **User Story 5 (P2)** → Multi-tenant (independent architecture pattern)
- **User Story 6 (P3)** → Dev tools (can develop independently, integrate later)
- **User Story 7 (P2)** → Production patterns (independent deployment configs)

### Recommended Sequence

**For MVP (minimum viable product)**:
1. Phase 1: Setup
2. Phase 2: Foundational
3. Phase 3: User Story 1 (expanded options) - CORE VALUE
4. Phase 4: User Story 2 (new categories) - CORE VALUE
5. Stop here for MVP validation

**For Full Feature**:
1-4 above, then:
5. Phase 5: User Story 3 (config builder)
6. Phase 6: User Story 4 (migration tool)
7. Phase 7: User Story 5 (multi-tenant)
8. Phase 8: User Story 6 (dev tools)
9. Phase 9: User Story 7 (production patterns)
10. Phase 10: Polish

### Parallel Opportunities

**After Foundational completes, these can run in parallel**:
- US1 (expanded options) + US2 (new categories) - different files, can work simultaneously
- US5 (multi-tenant) + US7 (production patterns) - independent patterns
- US6 (dev tools) - can develop independently

**Within each phase**:
- All tasks marked [P] can run in parallel
- Example: All database integration templates (T021-T024) can be created simultaneously
- Example: All auth integration templates (T037-T040) can be created simultaneously

---

## Parallel Example: User Story 1 (Expanded Options)

```bash
# Launch all database integrations together:
Task T021: "Create Neon integration template"
Task T022: "Create Supabase integration template"
Task T023: "Create PlanetScale integration template"
Task T024: "Create CockroachDB integration template"

# Launch all runtime frameworks together:
Task T025: "Create Next.js 16 runtime template"
Task T026: "Create Remix 2.x runtime template"
Task T027: "Create SvelteKit 2.x runtime template"
Task T028: "Create Astro 4.x runtime template"

# Parallel across categories:
Task T021-T024: Database expansion
Task T025-T028: Runtime expansion
Task T029-T032: Hosting expansion
Task T033-T036: ORM expansion
... all can proceed in parallel (different file paths)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

**Goal**: Expand from 28 to 80+ integrations - core value delivery

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T020) - CRITICAL GATE
3. Complete Phase 3: User Story 1 (T021-T058) - 56 integrations
4. Complete Phase 4: User Story 2 (T059-T100) - 24 more integrations
5. **STOP and VALIDATE**: Test expanded options, verify all 80+ integrations work
6. Deploy/demo expanded SaaS starter (MVP!)

**Value Delivered**: Developers can select from 4 options per category instead of 2, with 7 additional infrastructure categories. Core enhancement complete.

### Incremental Delivery

After MVP (US1 + US2), add value incrementally:

1. **Add User Story 3** (T101-T136): Visual config builder
   - Test independently: Launch config builder, export configs, verify they work with Copier
   - Deploy/demo: "Now with visual configuration!"

2. **Add User Story 4** (T137-T172): Migration tool
   - Test independently: Migrate one technology, verify app works, test rollback
   - Deploy/demo: "Now with technology migration!"

3. **Add User Story 5** (T173-T207): Multi-tenant patterns
   - Test independently: Generate multi-tenant app, verify tenant isolation
   - Deploy/demo: "Now with B2B multi-tenancy!"

4. **Add User Story 6** (T208-T241): Enhanced dev tools
   - Test independently: Run one-command setup, launch dashboard, test offline mode
   - Deploy/demo: "Now with enhanced developer experience!"

5. **Add User Story 7** (T242-T282): Production patterns
   - Test independently: Deploy to staging, verify multi-region failover, test DR procedures
   - Deploy/demo: "Now production-ready with enterprise patterns!"

### Parallel Team Strategy

With 4-6 developers after Foundational phase:

**Team A** (2 devs): User Story 1 (expanded options) + User Story 2 (new categories)
**Team B** (1 dev): User Story 5 (multi-tenant - independent pattern)
**Team C** (1 dev): User Story 7 (production patterns - independent deployment)
**Team D** (1 dev): User Story 6 (dev tools - independent utilities)

After US1+US2 complete:
**Team E** (1 dev): User Story 3 (config builder - needs US1+US2 data)
**Team F** (1 dev): User Story 4 (migration tool - needs US1+US2 integrations)

---

## Summary

**Total Tasks**: 300 tasks organized by 7 user stories
**MVP Tasks**: 100 tasks (Setup + Foundational + US1 + US2)
**Task Distribution**:
- Phase 1 (Setup): 10 tasks
- Phase 2 (Foundational): 10 tasks
- Phase 3 (US1 - P1): 38 tasks (56 integrations)
- Phase 4 (US2 - P1): 42 tasks (24 integrations)
- Phase 5 (US3 - P2): 36 tasks (config builder)
- Phase 6 (US4 - P2): 36 tasks (migration tool)
- Phase 7 (US5 - P2): 35 tasks (multi-tenant)
- Phase 8 (US6 - P3): 34 tasks (dev tools)
- Phase 9 (US7 - P2): 41 tasks (production patterns)
- Phase 10 (Polish): 18 tasks

**Parallel Opportunities**: 220+ tasks marked [P] can run in parallel within their phases

**Independent Testing**: Each user story has clear independent test criteria and can be validated standalone

**Suggested MVP**: Complete Phases 1-4 only (100 tasks) for core value delivery, then incrementally add remaining user stories based on priority

**Critical Path**: Setup → Foundational → US1 + US2 (parallel) → US3 + US4 (depends on US1+US2) → Remaining stories (mostly independent)

---

## Notes

- All tasks follow strict format: `- [ ] [ID] [P?] [Story] Description with file path`
- [P] indicates parallelizable tasks (different files, no dependencies)
- [Story] label (US1-US7) maps tasks to specific user stories for traceability
- Each user story phase is independently completable and testable
- Tests were NOT requested in specification, so test tasks are excluded
- File paths are absolute from repository root
- Commit after each logical group of tasks
- Stop at any checkpoint to validate story independently before proceeding
