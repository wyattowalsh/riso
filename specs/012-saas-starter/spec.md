# Feature Specification: SaaS Starter Template

**Feature Branch**: `012-saas-starter`  
**Created**: 2025-11-02  
**Status**: Draft  
**Input**: User description: "Create an optional saas-starter to be included in the template with configurable stack options for runtime, hosting, database, ORM, auth, enterprise bridge, billing, jobs, email, analytics, AI, storage, and CI/CD"

## Clarifications

### Session 2025-11-02

- Q: What observability and monitoring strategy should be included? → A: Comprehensive approach combining bundled observability platform (Sentry + Datadog), OpenTelemetry instrumentation, and structured logging with correlation IDs
- Q: How should secrets and API keys be managed securely? → A: Environment variables with validation; encrypted at rest in CI/CD; rotation documentation provided
- Q: What sample data and fixtures should be included? → A: Both seeded database fixtures with example SaaS entities AND factory/faker tooling for comprehensive data generation
- Q: How should database migrations be managed after initial generation? → A: ORM-native migration system (Prisma Migrate/Drizzle Kit) + CI validation + rollback procedures
- Q: What level of test coverage should be included? → A: Unit tests for business logic + integration tests for all service connections + E2E tests for critical user flows

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select and Generate SaaS Stack Configuration (Priority: P1)

A developer runs Copier on the Riso template and is prompted to enable the SaaS starter module. They are then presented with a series of binary choices for each infrastructure component (runtime, hosting, database, auth, etc.). After making selections, the template generates a fully integrated, production-ready SaaS application with all chosen services configured and connected.

**Why this priority**: This is the core value proposition - enabling rapid SaaS project initialization with informed technology choices. Without this, the feature has no value.

**Independent Test**: Can be fully tested by running the Copier template with the SaaS starter enabled, making all technology selections, and verifying that a runnable application is generated with all integrations functional.

**Acceptance Scenarios**:

1. **Given** a developer has Copier and the Riso template, **When** they enable the SaaS starter module during template rendering, **Then** they are presented with binary choices for each of the 13 infrastructure categories
2. **Given** the developer is viewing a category choice (e.g., "runtime"), **When** they review the options, **Then** they see exactly 2 options with clear labels and guidance on when to use each
3. **Given** the developer completes all selections, **When** the template finishes rendering, **Then** a working SaaS application is generated with all selected services properly integrated
4. **Given** the rendered application, **When** the developer runs the quickstart commands, **Then** the application starts successfully with authentication, database, and billing all functional

---

### User Story 2 - Understand Technology Trade-offs (Priority: P2)

A developer is choosing between two authentication providers (Clerk vs Auth.js). They can see clear guidance for each option explaining when to use it (e.g., "Clerk: Fastest DX, Next.js first, want orgs & agent-safe auth" vs "Auth.js: OSS-first, cost/control sensitive, simple OAuth"). This helps them make an informed decision aligned with their project needs.

**Why this priority**: Good technology decisions require context. This guidance prevents analysis paralysis and reduces post-generation regret. However, the feature can function without this if users already know their preferences.

**Independent Test**: Can be tested by reviewing the prompts during template rendering and verifying that each option includes actionable "use_when" guidance that differentiates the choices.

**Acceptance Scenarios**:

1. **Given** a developer is selecting between two options in any category, **When** they view the options, **Then** each option displays a "use_when" description that clearly differentiates when to choose it
2. **Given** a developer reads the guidance for both options, **When** they compare them, **Then** the guidance helps them identify which option aligns with their project constraints (team size, budget, technical requirements)
3. **Given** a developer is unsure which option to choose, **When** they select the default option, **Then** the default represents the most common/recommended choice for typical SaaS projects

---

### User Story 3 - Customize Configuration Post-Generation (Priority: P3)

After generating a SaaS application, a developer can view a configuration file (e.g., `saas-starter.config.ts`) that documents their selections. If they want to switch services (e.g., from Neon to Supabase), they can reference this configuration to understand what changes are needed and follow migration guidance.

**Why this priority**: While useful for understanding and potentially migrating technologies later, this is not essential for the initial value delivery. The generated code is the primary artifact.

**Independent Test**: Can be tested by generating an application, locating the configuration file, and verifying that it accurately reflects all selections made during template rendering.

**Acceptance Scenarios**:

1. **Given** a rendered SaaS application, **When** the developer opens the configuration file, **Then** they see all their technology selections documented with IDs, labels, and use-when guidance
2. **Given** a developer wants to change a technology choice post-generation, **When** they review the configuration file, **Then** they can identify which components need updating
3. **Given** the configuration file documents the choices, **When** team members join the project, **Then** they can quickly understand the technology stack decisions and rationale

---

### User Story 4 - Deploy to Production (Priority: P2)

A developer with a rendered SaaS application runs the deployment command. The application automatically deploys to the selected hosting platform (Vercel or Cloudflare) with all environment variables configured, database migrations run, and services connected. The application is immediately accessible with working authentication, billing, and data persistence.

**Why this priority**: Production deployment is critical for validating the full integration and delivering business value. However, local development must work first (P1), making this P2.

**Independent Test**: Can be tested by rendering an application with any combination of hosting/database/auth selections, running the deployment command, and verifying successful production deployment with all integrations functional.

**Acceptance Scenarios**:

1. **Given** a developer has a rendered SaaS application with Vercel hosting selected, **When** they run the deployment command, **Then** the application deploys to Vercel with all environment variables configured from their selections
2. **Given** the application is deployed, **When** a user visits the production URL, **Then** they can create an account, log in, and access a functioning dashboard
3. **Given** the application uses Stripe billing, **When** a user attempts to upgrade their plan, **Then** the Stripe integration processes the payment successfully
4. **Given** the application uses Neon database, **When** the user creates data, **Then** it persists correctly and is retrievable across sessions

---

### Edge Cases

- What happens when a developer selects incompatible options (e.g., Cloudflare hosting with Vercel-specific features)? The template should prevent invalid combinations or warn about limitations.
- How does the system handle missing API keys or credentials during deployment? The template should validate required environment variables and provide clear error messages with setup instructions.
- What happens when a selected service has a breaking API change? The template should pin to specific, tested versions and provide upgrade guidance separately.
- How does the application handle service outages (e.g., authentication provider down)? Each integration should include graceful degradation and user-friendly error messages.
- What happens when a developer wants to add a third option to a category (e.g., a new database provider)? The configuration structure should be extensible, though the template defaults to binary choices.
- How does the system handle rate limits or quotas on free tiers during development? The template should document tier limitations and suggest configuration for development vs. production.
- What happens when observability platforms (Sentry/Datadog) are down or have API issues? The application should buffer logs locally and retry with exponential backoff, ensuring core functionality continues even without telemetry.
- How are database migration conflicts resolved when multiple developers create migrations simultaneously? The ORM migration system should detect conflicts during CI validation and require manual merge resolution before deployment.
- What happens when seeded fixture data conflicts with user-created data in development? Fixtures should use deterministic IDs in a reserved range (e.g., 1-1000) with clear documentation to avoid ID collisions.
- How does the application handle API key rotation in production without downtime? Documentation should include blue-green credential rotation procedures with validation steps and rollback instructions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST present exactly 14 infrastructure categories during template rendering when SaaS starter is enabled (runtime, hosting, database, ORM, auth, enterprise bridge, billing, jobs, email, analytics, AI, storage, CI/CD, observability)
- **FR-002**: Each infrastructure category MUST offer exactly 2 options with no more than 2 choices per category
- **FR-003**: Each option MUST include an ID, human-readable label, and "use_when" guidance describing when to select that option
- **FR-004**: System MUST designate a default option for each category (the first option in the list)
- **FR-005**: System MUST validate that selected options are compatible with each other and warn about known limitations or incompatibilities
- **FR-006**: System MUST generate a working application with all selected services integrated and properly configured
- **FR-007**: Generated application MUST include environment variable templates with clear instructions for obtaining API keys and credentials for each selected service
- **FR-008**: Generated application MUST include a quickstart script that validates prerequisites, checks environment configuration, and starts the development environment
- **FR-009**: Generated application MUST include deployment scripts configured for the selected hosting platform (Vercel or Cloudflare)
- **FR-010**: System MUST generate database migration scripts compatible with the selected database and ORM combination
- **FR-011**: Generated application MUST include authentication flows (signup, login, logout, password reset) using the selected auth provider
- **FR-012**: Generated application MUST include billing integration with subscription plan creation and payment processing using the selected billing provider
- **FR-013**: Generated application MUST include working examples of background jobs using the selected job queue system
- **FR-014**: Generated application MUST include email templates and sending functionality using the selected email provider
- **FR-015**: Generated application MUST include analytics event tracking integrated with the selected analytics provider
- **FR-016**: Generated application MUST include AI integration examples using the selected AI provider
- **FR-017**: Generated application MUST include file storage integration using the selected storage provider
- **FR-018**: System MUST generate CI/CD workflow files configured for the selected CI/CD platform
- **FR-019**: Generated application MUST include health check endpoints for monitoring service availability
- **FR-020**: System MUST generate a configuration file documenting all technology selections and their rationale
- **FR-021**: Generated application MUST include comprehensive documentation covering setup, development workflow, deployment, and service-specific configuration
- **FR-022**: System MUST pin all dependencies to specific, tested versions to ensure reproducibility
- **FR-023**: Generated application MUST handle service initialization failures gracefully with clear error messages and setup instructions
- **FR-029**: Generated application MUST include comprehensive observability with bundled Sentry for error tracking and Datadog for APM, OpenTelemetry instrumentation for traces/metrics, and structured logging with correlation IDs across all services
- **FR-025**: Generated application MUST implement secure secrets management using environment variables with runtime validation, encryption at rest in CI/CD platforms (GitHub Secrets, Vercel/Cloudflare environment variables), and documentation for credential rotation procedures
- **FR-026**: Generated application MUST include seeded database fixtures with example SaaS entities (users, organizations, subscriptions, plans) AND factory/faker integration for programmatic test data generation
- **FR-027**: Generated application MUST use ORM-native migration system (Prisma Migrate or Drizzle Kit based on selection) with CI validation of migration safety and documented rollback procedures for production deployments
- **FR-028**: Generated application MUST include comprehensive test suite with unit tests for business logic, integration tests validating all service connections (database, auth, billing, jobs, email, storage, AI), and end-to-end tests covering critical user flows (signup, subscription, payment)
- **FR-029**: System MUST support the following specific technology combinations:
  - **Runtime**: Next.js 16 (React 19.2, Turbopack) OR Remix 2.x
  - **Hosting**: Vercel OR Cloudflare Pages + Workers + R2
  - **Database**: Neon serverless Postgres OR Supabase
  - **ORM**: Prisma OR Drizzle
  - **Auth**: Clerk OR Auth.js/NextAuth.js v5
  - **Enterprise Bridge**: WorkOS OR None
  - **Billing**: Stripe Billing 2025 OR Paddle
  - **Jobs**: Trigger.dev v4 OR Inngest
  - **Email**: Resend + React Email OR Postmark
  - **Analytics**: PostHog OR Amplitude
  - **AI**: OpenAI OR Anthropic Claude
  - **Storage**: Cloudflare R2 OR Supabase Storage
  - **CI/CD**: GitHub Actions → Vercel OR Cloudflare CI → Pages/Workers
  - **Observability**: Sentry + Datadog (bundled) with OpenTelemetry instrumentation
- **FR-030**: System MUST validate API key formats for all service integrations with service-specific validation rules (e.g., Stripe keys start with "sk_", Clerk keys match publishable/secret patterns, OpenAI keys start with "sk-")
- **FR-031**: Generated application MUST implement webhook signature verification for all services that send webhooks (Stripe, Clerk, Paddle, WorkOS) using service-specific signature validation libraries
- **FR-032**: Generated application MUST redact sensitive data (PII, credentials, tokens) from log output sent to observability platforms using configurable redaction patterns
- **FR-033**: Generated application MUST implement security headers (HSTS, X-Frame-Options, X-Content-Type-Options, CSP, Referrer-Policy, Permissions-Policy) configured appropriately for the selected hosting platform
- **FR-034**: Generated application MUST implement input validation and sanitization for all user inputs using Zod schemas to prevent injection attacks
- **FR-035**: Generated application MUST implement CSRF protection for all state-changing endpoints using framework-native CSRF token mechanisms
- **FR-036**: Generated application MUST implement rate limiting for API endpoints with configurable per-user and per-IP limits using the selected hosting platform's capabilities
- **FR-037**: Generated application MUST implement SQL injection prevention through exclusive use of ORM parameterized queries (no raw SQL strings with user input)
- **FR-038**: Generated application MUST implement XSS prevention through automatic HTML escaping in templates and Content Security Policy headers

### Key Entities

- **SaaS Starter Configuration**: Represents the complete set of technology selections made during template rendering, including version metadata, category choices with IDs and labels, and use-when guidance for each option
- **Infrastructure Category**: Represents one decision point in the stack (e.g., "database"), containing exactly 2 options with default designation, labels, IDs, and usage guidance
- **Technology Option**: Represents one selectable choice within a category, containing unique ID, human-readable label, and contextual guidance on when to use this option
- **Integration Template**: Represents the code and configuration generated for a specific technology selection, including service initialization, API client setup, environment variable mapping, and example usage
- **Environment Configuration**: Represents the collection of environment variables, API keys, and service credentials required for the selected technology stack to function, including validation rules, encryption metadata, and rotation schedules
- **Deployment Manifest**: Represents the hosting platform-specific configuration (Vercel config, Cloudflare Workers config) generated based on hosting selection
- **Observability Configuration**: Represents the telemetry setup including Sentry project configuration, Datadog API keys, OpenTelemetry exporter endpoints, log correlation settings, and trace sampling rules
- **Database Fixture Set**: Represents the seeded sample data including example users, organizations, subscription plans, and transactions with deterministic IDs and realistic attributes
- **Test Data Factory**: Represents the faker/factory configuration for programmatic test data generation with customizable entity builders and relationship management
- **Migration History**: Represents the database schema version control including migration files, rollback procedures, applied migration timestamps, and CI validation results
- **Accessibility Configuration**: Represents WCAG 2.1 Level AA compliance settings including ARIA labels, keyboard navigation handlers, focus indicators, color contrast ratios, and screen reader compatibility metadata
- **Rate Limit Policy**: Represents API rate limiting configuration including per-user limits, per-IP limits, time windows, burst allowances, and backoff strategies
- **Performance Baseline**: Represents measured performance characteristics including cold start times, p95/p99 request latencies, database query times, and resource utilization metrics
- **Cost Estimate**: Represents projected monthly costs broken down by service category (hosting, database, observability, integrations) at various user scales (1k, 10k, 100k users)
- **Deployment Strategy**: Represents the deployment approach including blue-green/canary settings, rollback procedures, health check configurations, and zero-downtime migration strategies
- **Circuit Breaker Configuration**: Represents fault tolerance settings including failure thresholds, timeout durations, half-open retry intervals, and fallback behaviors for each external service dependency

## Functional Requirements (Continued)

- **FR-049**: Generated application MUST implement WCAG 2.1 Level AA accessibility compliance including semantic HTML, ARIA labels, keyboard navigation for all interactive elements, focus indicators, and minimum 4.5:1 color contrast ratios
- **FR-050**: Generated application MUST implement webhook handler integration tests validating signature verification, event processing, idempotency, and error handling for all services supporting webhooks
- **FR-051**: Generated application MUST implement cross-service integration tests validating complete user flows (auth → database → billing → jobs → email) for each valid technology combination
- **FR-052**: System MUST generate configuration files documenting all technology selections, version numbers, API endpoints, environment variable requirements, and migration paths to alternative services
- **FR-053**: Generated application MUST implement blue-green deployment support with health checks, traffic routing, and automatic rollback on failed health checks
- **FR-054**: Generated application MUST implement database backup verification procedures with documented restore processes and recovery time objectives (RTO < 1 hour)
- **FR-055**: System MUST validate that dependency versions are pinned with exact version numbers (not ranges) in package.json and support automatic security updates through Dependabot
- **FR-056**: Generated application MUST implement log aggregation with structured JSON logging, correlation IDs linking related requests, and automatic log level adjustment based on environment (debug in dev, info in prod)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can render a complete SaaS application in under 5 minutes from running Copier command to having a working local development environment
- **SC-002**: Generated application starts successfully with all selected services functional within 2 minutes of running quickstart script (assuming credentials are configured)
- **SC-003**: 100% of the 14 infrastructure categories present exactly 2 options to choose from
- **SC-004**: Generated application passes all health checks for selected services (database connection, auth provider, billing API, etc.)
- **SC-005**: Developer can deploy to production within 10 minutes of completing local setup (assuming hosting platform account exists)
- **SC-006**: All 26 possible technology combinations (2^13 would be 8,192, but constrained by compatibility rules) generate working applications with no integration errors
- **SC-007**: Generated application includes working authentication flow allowing users to sign up, log in, and access protected content
- **SC-008**: Generated application includes working billing flow allowing users to subscribe to a plan and process payment
- **SC-009**: Generated application includes at least one working example of each selected service (job execution, email sending, analytics event, AI API call, file upload)
- **SC-010**: Documentation covers setup steps for all 26 technology options with service-specific configuration instructions
- **SC-011**: 90% of developers can complete initial setup without external support (measured by successful quickstart completion)
- **SC-012**: Generated applications achieve production deployment success rate of 95% on first attempt (assuming valid credentials)
- **SC-013**: All generated code passes quality checks (linting, type checking, tests) defined in the parent Riso template
- **SC-014**: Configuration file accurately documents all technology selections with IDs matching the actual generated integrations
- **SC-015**: Environment variable validation catches 100% of missing or invalid credentials before application startup
- **SC-016**: Generated CI/CD workflows successfully run tests and deploy to selected hosting platform
- **SC-017**: Average time from project generation to first paying customer is reduced by 50% compared to manual stack assembly
- **SC-018**: Generated application includes OpenTelemetry instrumentation with correlation IDs present in 100% of logged requests
- **SC-019**: Observability dashboards (Sentry + Datadog) are accessible and showing data within 5 minutes of first deployment
- **SC-020**: Environment variable validation detects 100% of missing or invalid credentials before application startup
- **SC-021**: Seeded fixtures include at least 5 example entities per major domain model (users, organizations, subscriptions)
- **SC-022**: Factory/faker tooling can generate 1000+ realistic test records in under 10 seconds
- **SC-023**: Database migrations execute successfully in CI with automated safety validation (no data loss detection)
- **SC-024**: Migration rollback procedures are tested and can restore previous schema state within 2 minutes
- **SC-025**: Test suite achieves minimum 70% code coverage with all service integrations validated
- **SC-026**: End-to-end test suite covers complete user journey from signup through first payment in under 3 minutes execution time
- **SC-027**: All generated code passes accessibility validation with 0 WCAG 2.1 Level AA violations using axe-core automated testing
- **SC-028**: Webhook signature verification prevents 100% of unauthorized webhook requests in integration tests
- **SC-029**: Security headers achieve A+ rating on securityheaders.com for all hosting platform deployments
- **SC-030**: Rate limiting successfully prevents abuse in load tests (blocks requests exceeding 100 req/min per user, 1000 req/min per IP)
- **SC-031**: Performance estimates accuracy within 20% of measured values in production for cold start and request latency
- **SC-032**: Database connection pooling prevents connection exhaustion under load (sustains 1000 concurrent users without errors)
- **SC-033**: Circuit breakers successfully prevent cascading failures in integration tests (service A failure doesn't crash service B)
- **SC-034**: Health check endpoints respond within 500ms and accurately report service availability (database, auth, billing APIs)
- **SC-035**: Structured logging includes correlation IDs in 100% of log entries allowing request tracing across services
- **SC-036**: Retry logic with exponential backoff successfully recovers from transient failures (99% success rate on 3rd attempt in chaos tests)
- **SC-037**: Generated applications achieve 99.9% uptime in production monitoring (measured over 30 days)
- **SC-038**: Deployment rollback procedures restore previous version within 5 minutes with zero data loss
- **SC-039**: API key validation catches 100% of invalid credentials before runtime (validates format at build time)
- **SC-040**: PII redaction successfully removes sensitive data from logs (0 credential leaks in audit of 1M log entries)
- **SC-041**: Documentation coverage includes troubleshooting guides for all ERROR-level compatibility issues with actionable fix suggestions

- Developers have accounts and access credentials for their selected services (Stripe API keys, Clerk publishable keys, etc.)
- Developers have basic familiarity with the selected technologies or can follow service-specific documentation
- The default option in each category represents the most popular/recommended choice for typical SaaS projects as of November 2025
- Service APIs remain stable within major versions; breaking changes will require template updates
- Hosting platforms (Vercel, Cloudflare) provide free tiers sufficient for development and testing
- All selected services support the latest LTS versions of Node.js and modern browsers
- Developers have Node.js 20+ and pnpm installed as prerequisites
- Template updates will be needed as services release new major versions or deprecate features
- Some technology combinations may have limitations documented in the compatibility validation layer
