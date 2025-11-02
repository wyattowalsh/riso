# Data Model: SaaS Starter Template

**Feature**: 012-saas-starter  
**Date**: 2025-11-02  
**Phase**: 1 - Design

## Overview

This document defines the data structures, entities, and relationships for the SaaS Starter Template feature. The data model encompasses both template-level entities (configuration, selections) and generated application entities (users, subscriptions, organizations).

---

## Template-Level Entities

### SaaSStarterConfiguration

Represents the complete set of technology selections made during Copier template rendering.

**Attributes:**
- `version`: string - Configuration schema version (e.g., "2025.11.02")
- `enabled`: boolean - Whether SaaS starter module is active
- `runtime`: TechnologyChoice - Selected runtime framework
- `hosting`: TechnologyChoice - Selected hosting platform
- `database`: TechnologyChoice - Selected database provider
- `orm`: TechnologyChoice - Selected ORM
- `auth`: TechnologyChoice - Selected auth provider
- `enterpriseBridge`: TechnologyChoice - Selected enterprise auth bridge (or "none")
- `billing`: TechnologyChoice - Selected billing provider
- `jobs`: TechnologyChoice - Selected job queue system
- `email`: TechnologyChoice - Selected email provider
- `analytics`: TechnologyChoice - Selected analytics platform
- `ai`: TechnologyChoice - Selected AI provider
- `storage`: TechnologyChoice - Selected storage provider
- `cicd`: TechnologyChoice - Selected CI/CD platform
- `observability`: ObservabilityConfiguration - Observability stack configuration

**Relationships:**
- Has many TechnologyChoice (one per category)
- Has one ObservabilityConfiguration

**Validation Rules:**
- All required categories must have a selection
- Selected technologies must pass compatibility validation
- Version must match current schema

**State Lifecycle:**
1. `uninitialized` - Before Copier prompts
2. `configuring` - During Copier prompt flow
3. `validated` - After compatibility check passes
4. `generated` - After template rendering completes

---

### TechnologyChoice

Represents a single technology selection within an infrastructure category.

**Attributes:**
- `categoryId`: string - Category identifier (e.g., "runtime", "database")
- `categoryLabel`: string - Human-readable category name
- `optionId`: string - Selected option identifier (e.g., "nextjs-16", "remix-2")
- `optionLabel`: string - Human-readable option name
- `useWhen`: string - Guidance text for when to use this option
- `isDefault`: boolean - Whether this is the default option for the category

**Relationships:**
- Belongs to SaaSStarterConfiguration

**Validation Rules:**
- optionId must be one of exactly 2 valid options for the category
- categoryId must be one of the 14 defined categories

---

### ObservabilityConfiguration

Represents the comprehensive observability stack configuration.

**Attributes:**
- `sentryEnabled`: boolean - Whether Sentry error tracking is enabled
- `sentryDsn`: string (optional) - Sentry project DSN
- `datadogEnabled`: boolean - Whether Datadog APM is enabled
- `datadogApiKey`: string (optional) - Datadog API key
- `datadogSite`: string - Datadog site (e.g., "datadoghq.com")
- `otelEnabled`: boolean - Whether OpenTelemetry instrumentation is enabled
- `otelExporterEndpoint`: string (optional) - Custom OTEL exporter endpoint
- `structuredLoggingEnabled`: boolean - Whether structured logging is configured
- `logLevel`: string - Minimum log level (debug, info, warn, error)
- `correlationIdStrategy`: string - How correlation IDs are generated (uuid, request-id, custom)

**Relationships:**
- Belongs to SaaSStarterConfiguration

**Validation Rules:**
- At least one observability component must be enabled
- If Sentry enabled, DSN must be provided or templated
- If Datadog enabled, API key must be provided or templated
- Log level must be one of: debug, info, warn, error

---

### IntegrationTemplate

Represents code and configuration files generated for a specific technology selection.

**Attributes:**
- `technologyId`: string - Technology identifier (e.g., "clerk", "stripe")
- `category`: string - Category this belongs to (auth, billing, etc.)
- `templateFiles`: array<TemplateFile> - List of Jinja2 template files to render
- `dependencies`: array<Dependency> - NPM/pip packages required
- `envVarRequirements`: array<EnvVarSpec> - Environment variables needed
- `configurationFiles`: array<string> - Config file paths to generate
- `exampleCode`: array<CodeExample> - Working code examples included

**Relationships:**
- References TechnologyChoice
- Has many TemplateFile
- Has many Dependency
- Has many EnvVarSpec

**Validation Rules:**
- All template files must exist in template directory
- Dependencies must specify version constraints
- EnvVarSpec must include validation rules

---

### CompatibilityRule

Represents compatibility validation between technology choices.

**Attributes:**
- `combination`: array<string> - Technology IDs that form this combination
- `severity`: string - "error" (blocks) or "warning" (allows with message)
- `message`: string - Explanation of compatibility issue
- `mitigation`: string (optional) - How to work around the limitation
- `recommendedAlternative`: string (optional) - Suggested compatible choice

**Relationships:**
- References multiple TechnologyChoice options

**Validation Rules:**
- Combination must have 2-4 technology IDs
- Severity must be "error" or "warning"
- Error-level rules must provide recommendedAlternative

---

## Generated Application Entities

These entities are included in the rendered SaaS application.

### User

Represents an authenticated user in the generated SaaS application.

**Attributes:**
- `id`: string (uuid/cuid) - Primary key
- `email`: string - User email (unique)
- `name`: string (optional) - User display name
- `avatarUrl`: string (optional) - Profile picture URL
- `emailVerified`: datetime (optional) - Email verification timestamp
- `role`: string - User role (user, admin, owner)
- `organizationMemberships`: array<OrganizationMembership> - Organizations this user belongs to
- `subscriptions`: array<Subscription> - User's personal subscriptions (if B2C)
- `createdAt`: datetime - Account creation timestamp
- `updatedAt`: datetime - Last modification timestamp

**Relationships:**
- Has many OrganizationMembership
- Has many Subscription (optional, for B2C SaaS)
- Has many ApiKey (for API access)
- Has many AuditLogEntry (for security tracking)

**Validation Rules:**
- Email must be valid format and unique
- Role must be one of: user, admin, owner
- At least one organization membership required (for B2B SaaS)

**State Lifecycle:**
1. `invited` - User invited but not yet signed up
2. `pending_verification` - Signed up, awaiting email verification
3. `active` - Verified and active
4. `suspended` - Temporarily disabled
5. `deleted` - Soft-deleted (for compliance)

---

### Organization

Represents a multi-tenant organization (for B2B SaaS).

**Attributes:**
- `id`: string (uuid/cuid) - Primary key
- `name`: string - Organization name
- `slug`: string - URL-safe identifier (unique)
- `logoUrl`: string (optional) - Organization logo
- `plan`: string - Subscription plan tier
- `maxSeats`: number - Maximum user seats allowed
- `currentSeats`: number - Currently used seats
- `metadata`: json - Custom organization metadata
- `createdAt`: datetime - Creation timestamp
- `updatedAt`: datetime - Last modification timestamp

**Relationships:**
- Has many OrganizationMembership
- Has one Subscription
- Has many WorkOSConnection (if enterprise bridge enabled)

**Validation Rules:**
- Slug must be URL-safe and unique
- currentSeats ≤ maxSeats
- Plan must be one of: starter, pro, enterprise

**State Lifecycle:**
1. `trial` - Free trial period
2. `active` - Paid subscription active
3. `past_due` - Payment failed, grace period
4. `suspended` - Subscription lapsed
5. `cancelled` - Organization deleted

---

### OrganizationMembership

Represents a user's membership in an organization with role-based permissions.

**Attributes:**
- `id`: string (uuid/cuid) - Primary key
- `userId`: string - Foreign key to User
- `organizationId`: string - Foreign key to Organization
- `role`: string - Member role (member, admin, owner)
- `invitedBy`: string (optional) - User ID who sent invitation
- `invitedAt`: datetime (optional) - Invitation timestamp
- `acceptedAt`: datetime (optional) - Acceptance timestamp
- `createdAt`: datetime - Creation timestamp

**Relationships:**
- Belongs to User
- Belongs to Organization

**Validation Rules:**
- userId + organizationId must be unique (one membership per user per org)
- Role must be one of: member, admin, owner
- Organization must have exactly one "owner" role
- If invitedAt is set, acceptedAt must be null or >= invitedAt

---

### Subscription

Represents a billing subscription (Stripe or Paddle).

**Attributes:**
- `id`: string (uuid/cuid) - Primary key
- `stripeSubscriptionId`: string (optional) - Stripe subscription ID
- `paddleSubscriptionId`: string (optional) - Paddle subscription ID
- `organizationId`: string (optional) - Foreign key to Organization (B2B)
- `userId`: string (optional) - Foreign key to User (B2C)
- `status`: string - Subscription status
- `plan`: string - Plan tier (starter, pro, enterprise)
- `billingCycle`: string - monthly or annual
- `currentPeriodStart`: datetime - Current billing period start
- `currentPeriodEnd`: datetime - Current billing period end
- `cancelAtPeriodEnd`: boolean - Whether subscription will cancel
- `trialEnd`: datetime (optional) - Trial expiration
- `metadata`: json - Custom subscription metadata
- `createdAt`: datetime - Creation timestamp
- `updatedAt`: datetime - Last modification timestamp

**Relationships:**
- Belongs to Organization (B2B) OR User (B2C)
- Has many UsageRecord (for metered billing)
- Has many Invoice

**Validation Rules:**
- Exactly one of stripeSubscriptionId or paddleSubscriptionId must be set
- Status must be one of: trialing, active, past_due, canceled, incomplete, incomplete_expired
- Either organizationId or userId must be set (not both)
- If status is "trialing", trialEnd must be set and in future

**State Lifecycle:**
1. `incomplete` - Subscription created, payment pending
2. `trialing` - In free trial period
3. `active` - Subscription active and paid
4. `past_due` - Payment failed, attempting retry
5. `canceled` - Subscription cancelled
6. `incomplete_expired` - Payment never completed, expired

---

### UsageRecord

Represents metered usage for usage-based billing (e.g., AI API calls).

**Attributes:**
- `id`: string (uuid/cuid) - Primary key
- `subscriptionId`: string - Foreign key to Subscription
- `metricName`: string - Usage metric (e.g., "ai_tokens", "api_calls")
- `quantity`: number - Usage amount
- `timestamp`: datetime - When usage occurred
- `metadata`: json - Additional usage context
- `reportedToProvider`: boolean - Whether synced to billing provider
- `createdAt`: datetime - Record creation timestamp

**Relationships:**
- Belongs to Subscription

**Validation Rules:**
- Quantity must be positive
- Metric name must be one of predefined metrics
- Timestamp must be within current billing period

---

### Invoice

Represents a billing invoice from Stripe or Paddle.

**Attributes:**
- `id`: string (uuid/cuid) - Primary key
- `subscriptionId`: string - Foreign key to Subscription
- `stripeInvoiceId`: string (optional) - Stripe invoice ID
- `paddleInvoiceId`: string (optional) - Paddle invoice ID
- `status`: string - Invoice status
- `amountDue`: number - Amount in cents
- `currency`: string - Currency code (USD, EUR, etc.)
- `pdfUrl`: string (optional) - PDF download URL
- `hostedInvoiceUrl`: string (optional) - Hosted page URL
- `dueDate`: datetime - Payment due date
- `paidAt`: datetime (optional) - Payment timestamp
- `createdAt`: datetime - Invoice creation timestamp

**Relationships:**
- Belongs to Subscription

**Validation Rules:**
- Exactly one of stripeInvoiceId or paddleInvoiceId must be set
- Status must be one of: draft, open, paid, void, uncollectible
- Amount due must be non-negative
- If status is "paid", paidAt must be set

---

### BackgroundJob

Represents a background job (Trigger.dev or Inngest).

**Attributes:**
- `id`: string (uuid/cuid) - Primary key
- `jobType`: string - Job type identifier (e.g., "send_welcome_email")
- `status`: string - Job status
- `payload`: json - Job input data
- `result`: json (optional) - Job output data
- `error`: string (optional) - Error message if failed
- `attempts`: number - Number of execution attempts
- `maxAttempts`: number - Maximum retry attempts
- `scheduledAt`: datetime (optional) - When job should run
- `startedAt`: datetime (optional) - Execution start time
- `completedAt`: datetime (optional) - Execution completion time
- `createdAt`: datetime - Job creation timestamp

**Relationships:**
- May belong to User or Organization (depends on job type)

**Validation Rules:**
- Status must be one of: pending, running, completed, failed, cancelled
- Attempts ≤ maxAttempts
- If status is "completed", completedAt must be set
- If status is "failed", error must be set

---

### ApiKey

Represents an API key for programmatic access to the SaaS application.

**Attributes:**
- `id`: string (uuid/cuid) - Primary key
- `userId`: string (optional) - Owner user ID
- `organizationId`: string (optional) - Owner organization ID
- `name`: string - Key name/description
- `keyHash`: string - Hashed API key (never store plain)
- `prefix`: string - First 8 chars of key (for identification)
- `scopes`: array<string> - Permissions granted to this key
- `lastUsedAt`: datetime (optional) - Last usage timestamp
- `expiresAt`: datetime (optional) - Expiration timestamp
- `revokedAt`: datetime (optional) - Revocation timestamp
- `createdAt`: datetime - Creation timestamp

**Relationships:**
- Belongs to User OR Organization

**Validation Rules:**
- keyHash must use secure hashing (bcrypt, argon2)
- At least one of userId or organizationId must be set
- Scopes must be from predefined set
- If revokedAt is set, key is invalid
- If expiresAt is set and past, key is invalid

---

### AuditLogEntry

Represents a security audit log entry for compliance and debugging.

**Attributes:**
- `id`: string (uuid/cuid) - Primary key
- `userId`: string (optional) - User who performed action
- `organizationId`: string (optional) - Organization context
- `action`: string - Action type (e.g., "user.login", "subscription.created")
- `resourceType`: string - Resource affected (e.g., "subscription", "api_key")
- `resourceId`: string (optional) - ID of affected resource
- `metadata`: json - Additional action context
- `ipAddress`: string (optional) - Request IP address
- `userAgent`: string (optional) - Request user agent
- `correlationId`: string (optional) - Request correlation ID
- `timestamp`: datetime - When action occurred

**Relationships:**
- May belong to User
- May belong to Organization

**Validation Rules:**
- Action must follow naming convention: `{resource}.{verb}`
- Timestamp must be immutable (never updated)
- Retention period: 90 days minimum for compliance

---

### SeededFixture

Represents deterministic seed data included in the generated application.

**Attributes:**
- `id`: string - Deterministic ID in reserved range (e.g., "seed-user-1")
- `entityType`: string - Type of entity (user, organization, subscription)
- `data`: json - Entity data
- `createdAt`: datetime - Fixture creation timestamp

**Relationships:**
- No direct relationships (fixtures are standalone)

**Validation Rules:**
- ID must be in reserved range (1-1000 or "seed-*" prefix)
- Entity type must be one of: user, organization, subscription, usage_record
- Data must conform to entity schema

---

## Relationships Diagram

```
SaaSStarterConfiguration
  ├─ TechnologyChoice (runtime)
  ├─ TechnologyChoice (hosting)
  ├─ TechnologyChoice (database)
  ├─ TechnologyChoice (orm)
  ├─ TechnologyChoice (auth)
  ├─ TechnologyChoice (enterpriseBridge)
  ├─ TechnologyChoice (billing)
  ├─ TechnologyChoice (jobs)
  ├─ TechnologyChoice (email)
  ├─ TechnologyChoice (analytics)
  ├─ TechnologyChoice (ai)
  ├─ TechnologyChoice (storage)
  ├─ TechnologyChoice (cicd)
  └─ ObservabilityConfiguration

Generated Application:

Organization
  ├─ OrganizationMembership (many)
  │   └─ User
  ├─ Subscription (one)
  │   ├─ UsageRecord (many)
  │   └─ Invoice (many)
  └─ ApiKey (many)

User
  ├─ OrganizationMembership (many)
  │   └─ Organization
  ├─ Subscription (many, if B2C)
  ├─ ApiKey (many)
  └─ AuditLogEntry (many)

BackgroundJob
  └─ User or Organization (optional)
```

---

## Index Strategy

For optimal query performance in generated applications:

**User Table:**
- Primary: `id` (uuid/cuid)
- Unique: `email`
- Index: `createdAt` (for pagination)

**Organization Table:**
- Primary: `id` (uuid/cuid)
- Unique: `slug`
- Index: `plan` (for filtering by tier)

**OrganizationMembership Table:**
- Primary: `id` (uuid/cuid)
- Unique: `(userId, organizationId)`
- Index: `organizationId` (for org member lookups)
- Index: `userId` (for user org lookups)

**Subscription Table:**
- Primary: `id` (uuid/cuid)
- Unique: `stripeSubscriptionId` OR `paddleSubscriptionId`
- Index: `organizationId` (for org subscription lookup)
- Index: `(status, currentPeriodEnd)` (for expiration checks)

**UsageRecord Table:**
- Primary: `id` (uuid/cuid)
- Index: `(subscriptionId, timestamp)` (for usage aggregation)
- Index: `(subscriptionId, reportedToProvider)` (for sync status)

**Invoice Table:**
- Primary: `id` (uuid/cuid)
- Index: `subscriptionId` (for subscription invoices)
- Index: `(status, dueDate)` (for payment reminders)

**BackgroundJob Table:**
- Primary: `id` (uuid/cuid)
- Index: `(status, scheduledAt)` (for job processing)
- Index: `jobType` (for job type filtering)

**ApiKey Table:**
- Primary: `id` (uuid/cuid)
- Unique: `keyHash`
- Index: `prefix` (for key identification)
- Index: `(organizationId, revokedAt IS NULL)` (for active org keys)

**AuditLogEntry Table:**
- Primary: `id` (uuid/cuid)
- Index: `userId` (for user activity logs)
- Index: `organizationId` (for org activity logs)
- Index: `(action, timestamp)` (for action filtering)
- Index: `correlationId` (for request tracing)

---

## Data Retention Policies

- **AuditLogEntry**: 90 days minimum (compliance), 1 year recommended
- **BackgroundJob**: 7 days for completed/failed, indefinite for pending
- **UsageRecord**: Retain for lifetime of subscription + 3 years (tax compliance)
- **Invoice**: Retain for lifetime + 7 years (financial compliance)
- **SeededFixture**: Never deleted (part of codebase)

---

## Migration Strategy

**Initial Setup:**
1. Run `prisma migrate dev` or `drizzle-kit push` to create tables
2. Run `pnpm seed` to populate fixtures
3. Validate with `pnpm test:integration:database`

**Schema Evolution:**
1. Update schema file (schema.prisma or schema.ts)
2. Generate migration: `prisma migrate dev --name <description>` or `drizzle-kit generate`
3. Review migration SQL for safety
4. Test migration on development database
5. Run CI validation to detect breaking changes
6. Deploy migration with rollback procedure documented

**Rollback Procedure:**
```sql
-- Prisma
BEGIN;
-- Apply reverse migration
DELETE FROM _prisma_migrations WHERE migration_name = '20250102_add_usage_records';
-- Restore schema
DROP TABLE usage_records;
COMMIT;

-- Drizzle
-- Manual rollback SQL based on generated migration
```

---

## Conclusion

This data model provides comprehensive structure for both template configuration (Copier-level) and generated application entities (SaaS-level). Key design decisions:

1. **Template entities** enable deterministic generation and compatibility validation
2. **Application entities** support both B2B (organization-centric) and B2C (user-centric) SaaS models
3. **Audit logging** ensures compliance and security tracking
4. **Usage metering** enables flexible billing models
5. **Seeded fixtures** provide realistic development data
6. **Index strategy** optimizes common query patterns

Next: Define API contracts for service integrations and template hooks.
