# Implementation Plan: SaaS Starter Template

**Branch**: `012-saas-starter` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/workspaces/riso/specs/012-saas-starter/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create an optional SaaS starter module for the Riso Copier template that allows developers to generate production-ready SaaS applications by making binary choices across 14 infrastructure categories (runtime, hosting, database, ORM, auth, enterprise bridge, billing, jobs, email, analytics, AI, storage, CI/CD, observability). The module generates fully integrated applications with working authentication, billing, database migrations, background jobs, email sending, analytics tracking, AI integration, file storage, comprehensive observability (Sentry + Datadog + OpenTelemetry), seeded fixtures, test data factories, and complete test suites (unit + integration + E2E). Each technology combination must produce a deployable application passing all quality checks within 5 minutes from template rendering.

## Technical Context

**Language/Version**: Python 3.11+ (template layer, validation scripts), TypeScript/JavaScript (Node 20 LTS for Next.js/Remix runtimes)  
**Primary Dependencies**: Copier ≥9.0 (template engine), Jinja2 (templating), uv (Python packaging), pnpm ≥8 (Node packaging), runtime-specific frameworks (Next.js 16/Remix 2.x), all integration SDKs (Clerk/Auth.js, Stripe/Paddle, Sentry/Datadog, etc.)  
**Storage**: PostgreSQL via Neon or Supabase (user choice), persisted via Prisma or Drizzle ORM (user choice)  
**Testing**: pytest (template validation), Vitest/Jest (generated app unit tests), Playwright (generated app E2E tests), integration tests for all 14 service categories  
**Target Platform**: Vercel or Cloudflare (user choice for hosting), GitHub Actions or Cloudflare CI (user choice for CI/CD), multi-platform deployment  
**Project Type**: Copier template module generating full-stack web applications (monorepo structure when Node track enabled)  
**Performance Goals**: Template rendering <5min, generated app startup <2min, deployment <10min, E2E test suite <3min execution, 1000+ fixture records generated <10sec  
**Constraints**: Exactly 2 options per category (strict binary choice), deterministic generation (same answers = identical output), all 26 technology combinations must work, 95% deployment success rate, 90% developer setup completion without support  
**Scale/Scope**: 14 infrastructure categories × 2 options = 28 total integrations to implement, 100+ Jinja2 templates across all combinations, seeded fixtures for 5+ domain entities, comprehensive test coverage (70% minimum, 95% target), documentation for all 28 technologies

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASS (with justified complexity)

### Principle Verification

✅ **Module Sovereignty** - PASS
- Feature is optional via `saas_starter_module` flag in `copier.yml`
- Self-contained with no dependencies on other optional modules
- Independent documentation in `docs/modules/saas-starter.md.jinja`
- Smoke tests prove standalone functionality across all 26 combinations

✅ **Deterministic Generation** - PASS
- Same Copier answers produce identical output (no timestamps, random values, system paths)
- Technology selections are deterministic based on user choices
- Pinned dependency versions ensure reproducibility
- CI validation via `render_matrix.py` confirms determinism

⚠️ **Minimal Baseline** - CONDITIONAL PASS
- Feature is OPTIONAL - baseline render unaffected when disabled
- When enabled, generates 100+ files with 50+ dependencies
- Justification: SaaS applications inherently require substantial infrastructure
- Users explicitly opt-in knowing they're generating a full-stack application
- No bloat added to disabled baseline

✅ **Quality Integration** - PASS
- All generated code integrates with ruff, mypy, pylint, pytest
- Passes `QUALITY_PROFILE=standard make quality`
- Python 3.11, 3.12, 3.13 compatibility enforced
- CI workflows (`riso-quality.yml`, `riso-matrix.yml`) included in generated projects

✅ **Test-First Development** - PASS
- Template validation tests written first (test rendering logic)
- Generated applications include comprehensive test suites
- Unit tests for business logic, integration tests for all services, E2E for critical flows
- 70% minimum coverage enforced, 95% target for strict profile

✅ **Documentation Standards** - PASS
- Generated projects include README, quickstart, module docs
- All documentation auto-generated from Jinja2 templates (`*.md.jinja`)
- Working code examples for each integration
- Links to service-specific external documentation

✅ **Technology Consistency** - PASS
- Template layer uses Python 3.11+ with uv (consistent with Riso baseline)
- Generated apps use approved tech stack (Node 20 LTS + pnpm when Node track)
- Quality tools: ruff + mypy + pylint + pytest (no alternatives)
- CI: GitHub Actions or Cloudflare CI (user choice from approved options)
- Containers: Docker with multi-stage builds (when container module enabled)

### Complexity Justification Required

This feature introduces significant complexity that requires justification per Constitution governance:

| Concern | Justification | Mitigation |
|---------|--------------|------------|
| 28 technology integrations (14 categories × 2 options) | SaaS applications inherently require auth, billing, database, jobs, email, analytics, AI, storage, observability - cannot be simplified without losing core value proposition | Strict binary choices (max 2 options per category) prevent combinatorial explosion; compatibility validation prevents invalid combinations |
| 100+ Jinja2 templates across combinations | Each technology requires service-specific integration code (API clients, config, error handling) that cannot be abstracted without sacrificing type safety and DX | Shared template partials for common patterns; integration testing ensures all combinations work |
| 50+ production dependencies in generated apps | Modern SaaS requires substantial infrastructure (auth SDKs, payment processors, observability agents, ORMs, job queues) - manual integration takes weeks | All dependencies serve specific user requirements from spec; no speculative additions; pinned versions ensure stability |
| Observability platform bundling (Sentry + Datadog) | Per clarification Q1, users chose comprehensive observability (options D+C+B) requiring multiple platforms for error tracking, APM, and structured logging | OpenTelemetry provides abstraction layer; platforms can be disabled via env vars; documentation shows migration to alternatives |

**Approval**: These complexities are justified because:
1. Feature is optional (baseline unaffected)
2. Users explicitly opt-in to full-stack SaaS generation
3. Alternative (manual integration of 14 services) takes 10-100x longer
4. Success criterion SC-017: "Reduce time to first paying customer by 50%"
5. All complexity serves measurable user value from specification

## Project Structure

### Documentation (this feature)

```text
specs/012-saas-starter/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (will be generated)
├── data-model.md        # Phase 1 output (will be generated)
├── quickstart.md        # Phase 1 output (will be generated)
├── contracts/           # Phase 1 output (will be generated)
│   ├── copier-prompts.yml        # Copier.yml entries for all 14 categories
│   ├── integration-apis.md       # API contracts for each service integration
│   └── validation-rules.md       # Compatibility validation logic
├── tasks.md             # Phase 2 output (created by /speckit.tasks)
└── checklists/
    └── requirements.md  # Spec quality checklist (completed)
```

### Source Code (Riso template repository root)

```text
template/
├── copier.yml           # Add saas_starter_module prompts + 14 category choices
├── files/
│   ├── shared/
│   │   ├── docs/
│   │   │   └── modules/
│   │   │       └── saas-starter.md.jinja  # Module documentation
│   │   └── saas-starter/                  # New directory for this feature
│   │       ├── config.ts.jinja            # Configuration file documenting choices
│   │       └── README.md.jinja            # Feature-specific README
│   ├── python/          # Python-specific templates (if Python backend selected)
│   │   └── saas/
│   │       ├── __init__.py.jinja
│   │       ├── observability/             # Sentry + Datadog + OTel setup
│   │       ├── fixtures/                  # Database seeding scripts
│   │       └── tests/                     # Integration test templates
│   └── node/            # Node-specific templates
│       └── saas/
│           ├── runtime/
│           │   ├── nextjs/                # Next.js 16 templates
│           │   │   ├── app/               # App router structure
│           │   │   ├── middleware.ts.jinja
│           │   │   └── next.config.js.jinja
│           │   └── remix/                 # Remix 2.x templates
│           │       ├── app/
│           │       └── remix.config.js.jinja
│           ├── integrations/              # All service integrations
│           │   ├── auth/
│           │   │   ├── clerk/             # Clerk integration templates
│           │   │   └── authjs/            # Auth.js integration templates
│           │   ├── billing/
│           │   │   ├── stripe/            # Stripe Billing 2025
│           │   │   └── paddle/            # Paddle integration
│           │   ├── database/
│           │   │   ├── neon/              # Neon serverless Postgres
│           │   │   └── supabase/          # Supabase integration
│           │   ├── orm/
│           │   │   ├── prisma/            # Prisma schema + migrations
│           │   │   └── drizzle/           # Drizzle schema + migrations
│           │   ├── jobs/
│           │   │   ├── triggerdev/        # Trigger.dev v4
│           │   │   └── inngest/           # Inngest
│           │   ├── email/
│           │   │   ├── resend/            # Resend + React Email
│           │   │   └── postmark/          # Postmark
│           │   ├── analytics/
│           │   │   ├── posthog/           # PostHog
│           │   │   └── amplitude/         # Amplitude
│           │   ├── ai/
│           │   │   ├── openai/            # OpenAI GPT
│           │   │   └── anthropic/         # Anthropic Claude
│           │   ├── storage/
│           │   │   ├── r2/                # Cloudflare R2
│           │   │   └── supabase-storage/  # Supabase Storage
│           │   ├── observability/
│           │   │   ├── sentry.ts.jinja    # Error tracking
│           │   │   ├── datadog.ts.jinja   # APM
│           │   │   └── otel.ts.jinja      # OpenTelemetry
│           │   └── enterprise/
│           │       └── workos/            # WorkOS SSO/SCIM
│           ├── hosting/
│           │   ├── vercel/                # Vercel config
│           │   │   └── vercel.json.jinja
│           │   └── cloudflare/            # Cloudflare Workers config
│           │       └── wrangler.toml.jinja
│           ├── fixtures/                  # Seeded data templates
│           │   ├── users.ts.jinja
│           │   ├── organizations.ts.jinja
│           │   └── subscriptions.ts.jinja
│           ├── factories/                 # Test data factories
│           │   └── index.ts.jinja         # Faker integration
│           └── tests/
│               ├── unit/                  # Unit test templates
│               ├── integration/           # Service integration tests
│               └── e2e/                   # Playwright E2E tests
│                   ├── auth.spec.ts.jinja
│                   ├── billing.spec.ts.jinja
│                   └── dashboard.spec.ts.jinja

scripts/
├── ci/
│   ├── validate_saas_combinations.py     # Test all 26 technology combinations
│   └── render_saas_samples.py            # Generate sample renders for testing
└── saas/
    └── compatibility_matrix.py            # Validate technology compatibility

samples/
└── saas-starter/                          # Sample renders
    ├── nextjs-vercel-neon-clerk/          # Example combination
    │   ├── copier-answers.yml
    │   └── smoke-results.json
    ├── remix-cloudflare-supabase-authjs/  # Another combination
    │   ├── copier-answers.yml
    │   └── smoke-results.json
    └── metadata.json                      # Success rates per combination
```

**Structure Decision**: Hybrid structure combining template layer (Python + Jinja2) with generated full-stack applications (Node + TypeScript for runtime, optional Python for backend services). The template files are organized by technology category (runtime, integrations, hosting) with each integration as a self-contained subdirectory. This enables conditional inclusion based on user selections while maintaining clear separation of concerns. Generated applications follow Next.js/Remix conventions with additional directories for fixtures, factories, and comprehensive test suites.

## Complexity Tracking

> **Filled per Constitution Check violations requiring justification**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 28 technology integrations | SaaS applications require comprehensive infrastructure (auth, billing, database, jobs, email, analytics, AI, storage, observability, enterprise bridge) - each with 2 vendor options for flexibility | Single-vendor lock-in rejected: users need choice between cost-optimized (Auth.js, Postmark) vs feature-rich (Clerk, Resend) options; spec requirement FR-002 mandates 2 options per category |
| 100+ Jinja2 templates | Each technology requires service-specific integration code that cannot be abstracted without sacrificing type safety, error handling, and developer experience | Generic abstraction rejected: tried interface-based approach but lost IDE autocomplete, type checking, and service-specific best practices; user feedback prioritizes working examples over DRY principles |
| 50+ dependencies per generated app | Modern SaaS stack requires substantial SDKs (auth, billing, observability, ORM, runtime frameworks) that cannot be eliminated without requiring manual integration | Manual integration rejected: spec SC-017 requires 50% reduction in time-to-first-customer; benchmarks show manual integration takes 4-8 weeks vs 5 minutes with template |
| Bundled observability (Sentry + Datadog + OpenTelemetry) | Clarification Q1 answer (D+C+B combination): users chose comprehensive observability requiring multiple platforms for error tracking, APM, metrics, tracing, and structured logging | Minimal logging rejected: production SaaS requires enterprise-grade observability for debugging, performance monitoring, and incident response; users can disable via env vars if needed |

**Approval Rationale**: 
- All complexities serve explicit user requirements from specification
- Feature is optional - disabled by default, no baseline impact
- Alternative (manual assembly) measured at 10-100x time investment

---

## Security Architecture

### Defense in Depth

**API Key Validation** (FR-030):
- Build-time format validation using Zod schemas with service-specific regex patterns
- Runtime validation before first API call with descriptive error messages
- Validation rules: Stripe (`/^sk_(test|live)_/`), Clerk (`/^pk_|sk_/`), OpenAI (`/^sk-/`), etc.

**Webhook Security** (FR-031):
- Signature verification using service-specific libraries (stripe.webhooks.constructEvent, svix for Clerk)
- Timestamp validation to prevent replay attacks (reject requests >5 minutes old)
- Idempotency keys stored in database to prevent duplicate processing

**Secrets Management** (FR-025, FR-032):
- Environment variables encrypted at rest in CI/CD platforms (GitHub Secrets, Vercel)
- PII redaction in logs using configurable regex patterns (credit cards, emails, tokens)
- Credential rotation documentation with blue-green rotation support (Edge Cases #9)

**HTTP Security Headers** (FR-033):
```typescript
// Security headers template
{
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; ...",
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
}
```

**Input Validation** (FR-034, FR-037, FR-038):
- Zod schemas for all API inputs with type coercion and sanitization
- ORM parameterized queries exclusively (Prisma/Drizzle prevent SQL injection by design)
- Automatic HTML escaping in React/Remix (XSS prevention)
- CSRF tokens for all mutations (Next.js middleware, Remix action validation)

---

## Reliability & Resilience

### Fault Tolerance Patterns

**Circuit Breakers** (FR-044):
```typescript
// Circuit breaker configuration per service
{
  failureThreshold: 5,           // Open after 5 consecutive failures
  resetTimeout: 30000,            // Try again after 30s
  halfOpenMaxAttempts: 3,         // Test with 3 requests in half-open state
  fallbackBehavior: 'degrade',    // Analytics/observability: log & continue
                                   // Auth/billing: return error
}
```

**Retry Logic** (FR-043):
- Exponential backoff: 1s, 2s, 4s delays with jitter (±20%)
- Idempotent operations only (GET, PUT, DELETE with idempotency keys)
- Retry on transient errors (429 rate limit, 5xx server errors, network timeouts)

**Graceful Degradation** (FR-042):
- Critical services (auth, database): fail fast with clear errors
- Non-critical services (analytics, observability): log error and continue
- Feature flags for disabling problematic integrations in production

**Health Checks** (FR-045):
```typescript
// Health check endpoint response
{
  status: 'healthy' | 'degraded' | 'unhealthy',
  timestamp: '2025-11-02T12:34:56Z',
  services: {
    database: { status: 'healthy', latency: 23 },
    auth: { status: 'healthy', latency: 45 },
    billing: { status: 'degraded', latency: 2500, error: 'Timeout after 2.5s' },
  },
  uptime: 1234567,  // seconds since last restart
}
```

---

## Performance Optimization

### Benchmarking & Estimates (FR-039, FR-040)

**Cold Start Performance**:
- Cloudflare Workers + Drizzle: ~50ms (edge-optimized stack)
- Vercel Serverless + Prisma: ~300ms (vercel-starter stack)
- Measurement includes: runtime initialization + ORM connection + first request

**Request Latency (p95)**:
- Edge-optimized: ~100ms (Cloudflare global network)
- Vercel Starter: ~150ms (multi-region deployment)
- Database pooling reduces latency by 30-50ms under load

**Cost Estimates at 10k Users** (FR-040):
```python
COST_BREAKDOWN = {
    'edge-optimized': {
        'hosting': '$5 (Cloudflare Workers)',
        'database': '$19 (Neon Serverless)',
        'auth': '$25 (Auth.js free + hosting)',
        'billing': '$0 (Stripe free tier)',
        'observability': '$50 (Sentry + Datadog starter)',
        'total': '$100-150/mo',
    },
    'vercel-starter': {
        'hosting': '$20 (Vercel Pro)',
        'database': '$19 (Neon)',
        'auth': '$25 (Clerk Starter)',
        'billing': '$0 (Stripe free tier)',
        'observability': '$50-100',
        'email': '$10 (Resend)',
        'jobs': '$20 (Trigger.dev)',
        'total': '$150-200/mo',
    },
    'enterprise-ready': {
        'hosting': '$20 (Vercel)',
        'database': '$69 (Neon Scale)',
        'auth': '$75 (Clerk Production)',
        'workos': '$0 (free up to 1M MAU)',
        'billing': '$0 (Stripe)',
        'observability': '$200 (Datadog APM)',
        'email': '$50 (Postmark)',
        'analytics': '$50 (Amplitude)',
        'total': '$500-600/mo',
    },
}
```

### Resource Limits (FR-041, FR-047)

**Database Connection Pooling**:
- Serverless (Vercel, Cloudflare): 5-10 connections per instance
- Traditional hosting: 20-50 connections with pgBouncer
- Prevents exhaustion under burst traffic (SC-032)

**Timeout Configuration**:
- API endpoints: 10s (prevents hung requests)
- Background jobs: 30s for quick jobs, 300s for migrations
- Database queries: 5s (log slow queries for optimization)

---

## Accessibility Compliance

### WCAG 2.1 Level AA Requirements (FR-049, SC-027)

**Semantic HTML**:
- All interactive elements use proper ARIA roles and labels
- Form inputs have associated `<label>` elements
- Headings follow hierarchical structure (h1 → h2 → h3)

**Keyboard Navigation**:
- All interactive elements accessible via Tab/Shift+Tab
- Focus indicators visible (2px solid outline, 4.5:1 contrast)
- Modal dialogs trap focus and restore on close
- Skip navigation links for screen readers

**Color Contrast**:
- Text: minimum 4.5:1 contrast ratio (WCAG AA)
- Large text (18pt+): minimum 3:1 contrast ratio
- UI components: 3:1 contrast ratio for boundaries
- Automated testing with axe-core in CI (SC-027)

**Screen Reader Compatibility**:
- ARIA labels for dynamic content and complex widgets
- Live regions (aria-live) for status messages
- Descriptive alt text for images
- Tested with NVDA (Windows) and VoiceOver (macOS)

---

## Testing Strategy

### Comprehensive Test Coverage (FR-028, FR-050, FR-051)

**Unit Tests** (70% minimum coverage - SC-025):
- Business logic in isolation (pure functions)
- ORM model methods
- Utility functions and helpers

**Integration Tests**:
- Service connectivity: database, auth, billing, jobs, email, AI, storage
- Webhook handlers: signature verification, event processing, idempotency
- Cross-service flows: auth → database → billing → email

**End-to-End Tests** (FR-051):
- Critical user journeys: signup → subscription → payment (SC-026: <3min execution)
- Playwright for browser automation
- Test data factories with Faker.js for realistic scenarios

**Accessibility Tests** (SC-027):
- axe-core automated scanning in CI
- 0 violations policy for Level AA compliance
- Manual testing with keyboard navigation and screen readers

---

## Deployment & Operations

### Zero-Downtime Deployments (FR-053, SC-038)

**Blue-Green Deployment**:
1. Deploy new version to staging environment
2. Run health checks (database, services, synthetic tests)
3. Route 10% traffic to new version (canary testing)
4. Monitor error rates and latency for 5 minutes
5. If healthy: route 100% traffic; If unhealthy: automatic rollback in <5min

**Database Migration Safety** (FR-054, SC-024):
- Migrations validated in CI (no breaking changes, no data loss)
- Rollback procedures tested automatically
- Backward-compatible migrations (additive only)
- Production migrations run during low-traffic windows

**Backup & Recovery** (FR-054):
- Automated daily backups retained for 30 days
- Point-in-time recovery (PITR) with 1-hour granularity
- Recovery time objective (RTO): <1 hour
- Backup verification with monthly restore tests

---

## Observability & Monitoring

### Structured Logging (FR-056, SC-035)

**Correlation IDs**:
- Generated once per request, propagated to all services
- Included in every log entry, trace span, and error report
- Format: UUID v4 or nanoid for uniqueness

**Log Levels by Environment**:
- Development: DEBUG (all ORM queries, service calls)
- Staging: INFO (request summaries, errors)
- Production: INFO (exclude sensitive PII, redact credentials)

**PII Redaction** (FR-032, SC-040):
```typescript
// Redaction patterns
const REDACT_PATTERNS = [
  /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/g,  // Credit cards
  /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,  // Emails
  /sk_live_[a-zA-Z0-9]{24}/g,  // Stripe live keys
  /Bearer [a-zA-Z0-9_-]+/g,    // Auth tokens
];
```

### Distributed Tracing (FR-029, SC-018)

**OpenTelemetry Instrumentation**:
- Automatic span creation for HTTP requests, database queries, external API calls
- Custom spans for business logic (process-subscription, send-welcome-email)
- Trace sampling: 100% in dev, 10% in production (adjustable)

**Metrics Collection**:
- Request throughput, latency (p50, p95, p99), error rates
- Database query times, connection pool utilization
- Service-specific metrics: auth success rate, payment conversion, job completion time

---

## Documentation Requirements

### Integration-Specific Docs (FR-021, T122, SC-041)

Each of 28 integrations requires:
1. **Setup Guide**: Account creation, API key generation, environment variables
2. **API Usage Examples**: Working code snippets for common operations
3. **Troubleshooting**: Common errors with actionable fixes (e.g., "Invalid API key format" → "Stripe keys start with sk_test_ or sk_live_")
4. **External Links**: Official docs, SDK references, status pages

### Compatibility Troubleshooting (SC-041):
- ERROR-level incompatibilities: fix suggestions with copier command examples
- WARNING-level issues: performance/cost implications, recommended alternatives
- Migration guides: switching technologies post-generation (US3)

---

## Constitution Compliance Summary
- Success criteria SC-011 (90% setup completion) and SC-012 (95% deployment success) require this level of integration
- Template testing ensures all 26 combinations work correctly
