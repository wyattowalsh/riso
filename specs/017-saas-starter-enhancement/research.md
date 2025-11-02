# Phase 0: Research & Technology Decisions

**Feature**: 017-saas-starter-enhancement  
**Date**: 2025-11-02  
**Status**: Completed

## Research Overview

This document consolidates research findings for all technology decisions required by the SaaS Starter Comprehensive Enhancement. Research covers: (1) Expanded technology options for existing categories, (2) New infrastructure categories and their technology options, (3) Configuration builder implementation approaches, (4) Migration tool architecture patterns, (5) Multi-tenant isolation strategies, (6) Production deployment patterns, and (7) Enhanced developer tooling approaches.

## Category 1: Expanded Technology Options (Original Categories)

### 1.1 Database Options (Expand from 2 to 4)

**Decision**: Add PlanetScale and CockroachDB alongside existing Neon and Supabase

**Original Options**:
- Neon: Serverless Postgres with branching
- Supabase: Open-source Firebase alternative with Postgres

**New Options Research**:

**PlanetScale**:
- **Technology**: MySQL-compatible serverless database with vitess architecture
- **Key Features**: Database branching, non-blocking schema changes, horizontal sharding, connection pooling
- **Use When**: Need MySQL compatibility, horizontal scaling critical, team comfortable with vitess workflows
- **Pricing**: Free tier: 5GB storage, 1B row reads/month; paid from $39/month
- **Integration**: Works with Prisma and Drizzle ORM; requires MySQL-specific query syntax
- **Best Practices**: Use PlanetScale CLI for schema migrations; leverage query insights for optimization
- **Alternatives Considered**: Render PostgreSQL (rejected - not serverless), Railway MySQL (rejected - smaller ecosystem)

**CockroachDB**:
- **Technology**: Distributed PostgreSQL-compatible database with multi-region support
- **Key Features**: Strong consistency, multi-region writes, automatic replication, survivability guarantees
- **Use When**: Need multi-region deployment, strong consistency required, regulatory data residency requirements
- **Pricing**: Free tier: 5GB storage, 50M RUs/month; serverless from $1/million requests
- **Integration**: PostgreSQL-compatible; works with Prisma and Drizzle; some PostgreSQL extensions unsupported
- **Best Practices**: Use follower reads for latency optimization; configure survival goals per table
- **Alternatives Considered**: YugabyteDB (rejected - more complex), Spanner (rejected - Google Cloud lock-in)

**Rationale**: These additions provide clear differentiation:
- Neon: Best DX, branching workflows
- Supabase: Open-source, all-in-one platform
- PlanetScale: MySQL, horizontal sharding
- CockroachDB: Multi-region, strong consistency

### 1.2 Authentication Options (Expand from 2 to 4)

**Decision**: Add WorkOS and Supabase Auth alongside existing Clerk and Auth.js

**Original Options**:
- Clerk: User management with organizations, embeddable UI components
- Auth.js: Open-source authentication library (formerly NextAuth.js)

**New Options Research**:

**WorkOS**:
- **Technology**: Enterprise authentication platform focused on B2B SaaS
- **Key Features**: SAML SSO, SCIM provisioning, Directory Sync, MFA, audit logs
- **Use When**: Building B2B SaaS, need enterprise SSO (Okta, Azure AD), SCIM provisioning required
- **Pricing**: Free up to 1M MAUs; paid features (SSO, SCIM) from $125/month per connection
- **Integration**: SDKs for Node.js, React, Next.js; webhook support for user events
- **Best Practices**: Combine with Clerk/Auth.js for consumer auth; use WorkOS for enterprise customers only
- **Alternatives Considered**: Auth0 (rejected - expensive), Frontegg (rejected - smaller ecosystem)

**Supabase Auth**:
- **Technology**: Open-source authentication service integrated with Supabase platform
- **Key Features**: Email/password, OAuth providers, magic links, phone auth, RLS integration
- **Use When**: Already using Supabase database/storage, want all-in-one platform, need tight RLS integration
- **Pricing**: Included with Supabase; unlimited users on all plans
- **Integration**: Native integration with Supabase database row-level security
- **Best Practices**: Leverage RLS policies for authorization; use service role key sparingly
- **Alternatives Considered**: Firebase Auth (rejected - Firebase lock-in), AWS Cognito (rejected - poor DX)

**Rationale**: These additions provide clear use cases:
- Clerk: Consumer SaaS, best DX
- Auth.js: Open-source, full control, cost-sensitive
- WorkOS: Enterprise B2B, SSO/SCIM required
- Supabase Auth: Supabase ecosystem, all-in-one platform

### 1.3 Storage Options (Expand from 2 to 4)

**Decision**: Add AWS S3 and UploadThing alongside existing Cloudflare R2 and Supabase Storage

**Original Options**:
- Cloudflare R2: S3-compatible object storage with zero egress fees
- Supabase Storage: Open-source storage with RLS and image transformations

**New Options Research**:

**AWS S3**:
- **Technology**: Industry-standard object storage service
- **Key Features**: 99.999999999% durability, lifecycle policies, versioning, event notifications, glacier archival
- **Use When**: Need AWS ecosystem integration, industry-standard choice, require glacier archival, high durability critical
- **Pricing**: $0.023/GB storage, $0.09/GB egress (first 10TB); free tier: 5GB storage, 20K GET, 2K PUT
- **Integration**: AWS SDK for JavaScript, pre-signed URLs, CloudFront CDN integration
- **Best Practices**: Use CloudFront for CDN, lifecycle policies for cost optimization, S3 Transfer Acceleration for uploads
- **Alternatives Considered**: Google Cloud Storage (rejected - GCP lock-in), MinIO (rejected - self-hosted complexity)

**UploadThing**:
- **Technology**: Developer-first file upload service with type-safe APIs
- **Key Features**: Type-safe uploads, built-in UI components, image optimization, video processing, webhooks
- **Use When**: Need simple file upload UX, want type-safe API, require image/video processing, small-medium file volumes
- **Pricing**: Free: 2GB storage, 10GB bandwidth; pro from $10/month for 100GB
- **Integration**: React components, Next.js app router support, tRPC integration
- **Best Practices**: Use upload drop zones, configure allowed file types, leverage webhooks for post-processing
- **Alternatives Considered**: Uploadcare (rejected - expensive), Filestack (rejected - legacy API)

**Rationale**: These additions provide clear differentiation:
- Cloudflare R2: Zero egress, edge network
- Supabase Storage: Supabase ecosystem, RLS integration
- AWS S3: Industry standard, AWS ecosystem, glacier archival
- UploadThing: Best DX, type-safe, built-in UI

### 1.4 Email Options (Expand from 2 to 4)

**Decision**: Add SendGrid and AWS SES alongside existing Resend and Postmark

**Original Options**:
- Resend: Modern email API with React Email integration
- Postmark: Transactional email specialist with high deliverability

**New Options Research**:

**SendGrid**:
- **Technology**: Enterprise email platform with marketing and transactional capabilities
- **Key Features**: Transactional + marketing emails, email analytics, A/B testing, dynamic templates, suppression management
- **Use When**: Need both transactional and marketing emails, require detailed analytics, enterprise scale (millions of emails)
- **Pricing**: Free: 100 emails/day; essentials from $19.95/month for 50K emails
- **Integration**: Official SDKs for Node.js, webhook events, template engine
- **Best Practices**: Separate transactional and marketing sending; use subuser accounts for isolation
- **Alternatives Considered**: Mailgun (rejected - less reliable), Mailchimp (rejected - marketing focus)

**AWS SES**:
- **Technology**: AWS Simple Email Service for bulk and transactional email
- **Key Features**: High volume sending, pay-as-you-go pricing, tight AWS integration, SMTP interface
- **Use When**: High email volume (100K+ per day), AWS ecosystem, cost optimization critical, SMTP required
- **Pricing**: $0.10 per 1,000 emails sent; free tier: 62K emails/month (when from EC2)
- **Integration**: AWS SDK, SMTP interface, SNS notifications for bounces/complaints
- **Best Practices**: Warm up sending reputation gradually, monitor bounce/complaint rates, use configuration sets
- **Alternatives Considered**: SparkPost (rejected - complex pricing), Elastic Email (rejected - deliverability concerns)

**Rationale**: These additions provide clear use cases:
- Resend: Modern DX, React Email integration
- Postmark: Best deliverability, transactional specialist
- SendGrid: Enterprise scale, marketing + transactional
- AWS SES: High volume, AWS ecosystem, lowest cost

### 1.5 AI Options (Expand from 2 to 4)

**Decision**: Add Google Gemini and Ollama (local LLMs) alongside existing OpenAI and Anthropic

**Original Options**:
- OpenAI: GPT-4, ChatGPT API, function calling, vision, DALL-E
- Anthropic: Claude 3 models, 200K context, computer use

**New Options Research**:

**Google Gemini**:
- **Technology**: Google's multimodal AI models (Gemini Pro, Gemini Ultra)
- **Key Features**: Native multimodal (text, image, audio, video), long context (1M+ tokens in Gemini 1.5), Google workspace integration
- **Use When**: Need multimodal capabilities, long context windows (>200K tokens), Google Cloud ecosystem, cost optimization
- **Pricing**: Gemini Pro: $0.50/$1.50 per 1M tokens (input/output); free tier available
- **Integration**: Official Node.js SDK, Vertex AI integration, streaming support
- **Best Practices**: Use Gemini 1.5 Pro for long context, leverage multimodal for document analysis, cache prompts for cost optimization
- **Alternatives Considered**: Cohere (rejected - smaller model selection), AI21 Labs (rejected - less adoption)

**Ollama (Local LLMs)**:
- **Technology**: Local LLM runtime supporting Llama 3, Mistral, CodeLlama, and other open models
- **Key Features**: Fully local/offline operation, no API costs, data privacy, multiple model support, Docker deployment
- **Use When**: Data privacy critical, want zero API costs, offline operation required, development/testing environments
- **Pricing**: Free (hardware costs only); requires GPU for reasonable performance
- **Integration**: REST API compatible with OpenAI SDK, streaming support, model management CLI
- **Best Practices**: Use Llama 3.1 8B for development, 70B for production quality; configure GPU acceleration; implement fallback to cloud APIs for production
- **Alternatives Considered**: LM Studio (rejected - GUI focus), LocalAI (rejected - less maintained)

**Rationale**: These additions provide clear differentiation:
- OpenAI: Industry standard, best function calling
- Anthropic: Largest context (200K), Claude quality
- Gemini: Multimodal, long context (1M+), cost-effective
- Ollama: Local/offline, zero API cost, privacy

## Category 2: New Infrastructure Categories

### 2.1 Search (New Category - 3 Options)

**Decision**: Algolia, Meilisearch, Typesense

**Algolia**:
- **Technology**: Hosted search-as-a-service with typo tolerance and faceted search
- **Key Features**: Sub-50ms search, typo tolerance, faceting/filtering, analytics, A/B testing, merchandising rules
- **Use When**: Need best-in-class search UX, can afford premium pricing, require analytics and A/B testing
- **Pricing**: Free: 10K searches, 10K records; from $1/month for 100K searches
- **Integration**: InstantSearch.js, React components, REST API, realtime indexing
- **Best Practices**: Use replica indices for different sort orders, configure ranking formula per use case, leverage query suggestions
- **Performance**: <50ms p95 latency, globally distributed, 99.99% SLA

**Meilisearch**:
- **Technology**: Open-source, typo-tolerant search engine written in Rust
- **Key Features**: Instant search results (<50ms), typo tolerance, filtering, faceting, self-hosted or cloud
- **Use When**: Want open-source, cost-sensitive, need good performance, comfortable self-hosting or use Meilisearch Cloud
- **Pricing**: Free (self-hosted); Meilisearch Cloud from $30/month
- **Integration**: Official SDKs (JavaScript, Python, PHP, etc.), instant-search UI components
- **Best Practices**: Configure filterable/sortable attributes at index creation, use tenant tokens for multi-tenancy, tune relevancy with ranking rules
- **Performance**: <50ms typical latency (self-hosted on good hardware)

**Typesense**:
- **Technology**: Fast, typo-tolerant search engine with geo-search and faceting
- **Key Features**: <50ms search, geo search, faceting, synonym support, vector search, self-hosted or cloud
- **Use When**: Need geo-search, vector search for semantic queries, open-source with commercial support, moderate pricing
- **Pricing**: Free (self-hosted); Typesense Cloud from $50/month for 4GB
- **Integration**: Official SDKs, InstantSearch adapter, REST API
- **Best Practices**: Use collection aliases for zero-downtime reindexing, configure faceting fields carefully, leverage caching headers
- **Performance**: <50ms p95 latency, horizontally scalable

**Rationale**: Three options balance features, cost, and control:
- Algolia: Premium, best UX, analytics/merchandising
- Meilisearch: Open-source, self-hosted, cost-effective
- Typesense: Geo-search, vector search, balanced pricing

**Alternatives Considered**: Elasticsearch (rejected - too complex for SaaS starter), Amazon CloudSearch (rejected - AWS lock-in)

### 2.2 Cache (New Category - 3 Options)

**Decision**: Redis (Upstash), Cloudflare KV, Vercel KV

**Redis (Upstash)**:
- **Technology**: Serverless Redis with REST API and global replication
- **Key Features**: Redis-compatible API, REST interface, geo-replication, durable storage, pub/sub, streams
- **Use When**: Need full Redis capabilities (sorted sets, pub/sub, streams), serverless pricing model, multi-region replication
- **Pricing**: Free: 10K commands/day; pay-as-you-go from $0.2 per 100K commands
- **Integration**: Standard Redis clients, REST API for edge compatibility, Vercel integration
- **Best Practices**: Use pipelines for batch operations, configure TTLs appropriately, leverage pub/sub for realtime features
- **Performance**: <10ms p95 latency, auto-scaling

**Cloudflare KV**:
- **Technology**: Eventually-consistent key-value store at Cloudflare's edge
- **Key Features**: Global replication to 300+ locations, eventually consistent, unlimited reads from cache
- **Use When**: Need edge caching, can tolerate eventual consistency, Cloudflare Workers deployment, unlimited read scale
- **Pricing**: Free: 100K reads/day, 1K writes/day; paid: $0.50 per million reads, $5 per million writes
- **Integration**: Workers KV binding, REST API, automatic geo-replication
- **Best Practices**: Treat as eventually consistent (60s+ propagation), use for static/infrequently updated data, leverage unlimited cached reads
- **Performance**: <1ms p50 latency (cached), ~15ms (cache miss)

**Vercel KV**:
- **Technology**: Durable Redis powered by Upstash, integrated with Vercel
- **Key Features**: Redis-compatible, serverless, Vercel-optimized, connection pooling, global replication
- **Use When**: Deploying to Vercel, want tight integration, need Redis compatibility, serverless pricing preferred
- **Pricing**: Included in Vercel Pro ($20/month); pay-as-you-go above limits
- **Integration**: @vercel/kv SDK, automatic connection management, Edge Runtime compatible
- **Best Practices**: Use Edge SDK for edge functions, leverage connection pooling, monitor usage in Vercel dashboard
- **Performance**: <10ms p95 latency from Vercel functions

**Rationale**: Three options cover different deployment targets:
- Redis (Upstash): Full Redis features, multi-platform
- Cloudflare KV: Edge caching, Cloudflare Workers
- Vercel KV: Vercel-optimized, tight integration

**Alternatives Considered**: DynamoDB (rejected - AWS lock-in, higher latency), Momento (rejected - newer, less proven)

### 2.3 Feature Flags (New Category - 3 Options)

**Decision**: LaunchDarkly, PostHog Feature Flags, GrowthBook

**LaunchDarkly**:
- **Technology**: Enterprise feature flag and experimentation platform
- **Key Features**: Instant flag changes, targeting rules, A/B experiments, flag dependencies, audit logs, workflow approvals
- **Use When**: Need enterprise features (approvals, audit logs), complex targeting rules, experiments at scale, compliance requirements
- **Pricing**: Free: 1K MAUs; paid from $8.33/seat/month + usage
- **Integration**: SDKs for all platforms, React hooks, SSR support, Jira/GitHub integration
- **Best Practices**: Use environments for staging/production, implement flag cleanup process, leverage targeting rules over code branches
- **Performance**: <100ms flag evaluation, local caching, streaming updates

**PostHog Feature Flags**:
- **Technology**: Open-source product analytics with integrated feature flags
- **Key Features**: Feature flags, A/B testing, analytics integration, session replay, free for moderate usage
- **Use When**: Already using PostHog for analytics, want unified platform, cost-sensitive, open-source preferred
- **Pricing**: Free: 1M events/month; paid from $0.000045/event above free tier
- **Integration**: JavaScript SDK, React hooks, backend SDKs (Python, Node.js, Go)
- **Best Practices**: Use feature flags with analytics to track impact, leverage session replay for debugging, implement local evaluation for performance
- **Performance**: <50ms flag evaluation (with local caching)

**GrowthBook**:
- **Technology**: Open-source feature flagging and experimentation platform with warehouse-native approach
- **Key Features**: A/B testing, feature flags, Bayesian statistics, warehouse-native (queries your data warehouse), self-hosted or cloud
- **Use When**: Have existing data warehouse, want statistical rigor in experiments, cost-sensitive, prefer self-hosting
- **Pricing**: Free (self-hosted); cloud from $20/month for 3 users
- **Integration**: SDKs for React, Node.js, Python; edge SDK for Cloudflare Workers/Vercel Edge
- **Best Practices**: Use SDK caching for performance, connect to data warehouse for experiment analysis, implement gradual rollouts
- **Performance**: <10ms flag evaluation (with client-side caching)

**Rationale**: Three options balance features, cost, and integration:
- LaunchDarkly: Enterprise features, compliance, complex workflows
- PostHog: Unified analytics + flags, cost-effective
- GrowthBook: Open-source, warehouse-native, statistical rigor

**Alternatives Considered**: Unleash (rejected - less mature), Split (rejected - expensive), Statsig (rejected - newer)

### 2.4 CMS (New Category - 4 Options)

**Decision**: Contentful, Sanity, Payload CMS, Strapi

**Contentful**:
- **Technology**: API-first headless CMS with content modeling and localization
- **Key Features**: Powerful content modeling, localization, workflow/publishing, CDN delivery, GraphQL + REST APIs
- **Use When**: Need enterprise CMS, complex content models, multi-language content, large content teams
- **Pricing**: Free: 2 users, 25K records, 1M API calls/month; team from $489/month
- **Integration**: JavaScript SDK, GraphQL API, webhooks, Next.js integration
- **Best Practices**: Design content models early, use references for relationships, leverage CDN caching, implement preview mode
- **Performance**: <100ms content delivery via CDN

**Sanity**:
- **Technology**: Platform for structured content with real-time collaboration
- **Key Features**: Real-time editing, portable text, image pipeline, GROQ query language, Studio customization
- **Use When**: Need real-time collaboration, custom editing experience, image optimization, flexible content structure
- **Pricing**: Free: 3 users, unlimited documents, 10GB bandwidth/month; from $99/month for teams
- **Integration**: JavaScript client, GROQ API, React components, Next.js integration, webhooks
- **Best Practices**: Define schemas with TypeScript, use GROQ for flexible queries, leverage image pipeline (transforms, hotspots), implement incremental static regeneration
- **Performance**: <50ms query latency, global CDN

**Payload CMS**:
- **Technology**: TypeScript-based headless CMS that integrates with Next.js
- **Key Features**: Code-first configuration, type-safe, self-hosted, React admin panel, access control, file uploads
- **Use When**: Want type-safety, prefer code configuration, need full control (self-hosted), tight Next.js integration
- **Pricing**: Free (self-hosted); Payload Cloud from $25/month
- **Integration**: Built with Next.js, TypeScript config, React admin UI, automatic API generation
- **Best Practices**: Define collections in code, use hooks for business logic, leverage automatic TypeScript types, implement access control policies
- **Performance**: Self-hosted performance depends on hosting; API responds in <100ms typically

**Strapi**:
- **Technology**: Open-source headless CMS with admin panel
- **Key Features**: Customizable admin panel, plugin system, role-based access control, internationalization, media library
- **Use When**: Need open-source, want admin UI out-of-the-box, prefer self-hosting, require plugin extensibility
- **Pricing**: Free (self-hosted); Strapi Cloud from $99/month
- **Integration**: REST + GraphQL APIs, SDKs for popular frameworks, plugin marketplace
- **Best Practices**: Use content-types builder for rapid prototyping, implement field-level permissions, leverage draft/publish workflow, configure media library providers
- **Performance**: Self-hosted; API typically <100ms with proper database indexing

**Rationale**: Four options cover different use cases:
- Contentful: Enterprise, complex models, localization
- Sanity: Real-time, custom editing, image optimization
- Payload: Type-safe, Next.js-native, code-first
- Strapi: Open-source, plugin ecosystem, admin UI

**Alternatives Considered**: Ghost (rejected - blog focus), Prismic (rejected - less flexible), Butter CMS (rejected - expensive)

### 2.5 Usage Metering (New Category - 3 Options)

**Decision**: Stripe Metering, Moesif, Amberflo

**Stripe Metering**:
- **Technology**: Native usage metering integrated with Stripe Billing
- **Key Features**: Real-time metering, automatic billing, multiple aggregation methods (sum, max, last), usage reporting
- **Use When**: Already using Stripe Billing, need tight billing integration, simple metering requirements
- **Pricing**: Included with Stripe Billing; standard Stripe transaction fees apply
- **Integration**: Stripe API, webhooks, Stripe Dashboard for reporting
- **Best Practices**: Report usage events in real-time, use idempotency keys, aggregate locally before reporting, implement usage caps
- **Performance**: API accepts millions of meter events per day

**Moesif**:
- **Technology**: API analytics and monetization platform with usage-based billing
- **Key Features**: API analytics, usage metering, user tracking, billing integrations (Stripe, Zuora), governance dashboards
- **Use When**: Need detailed API analytics alongside metering, complex usage tracking, want to monetize APIs
- **Pricing**: Free: 10K events/month; growth from $499/month
- **Integration**: Middleware/SDKs for all platforms, Stripe/Zuora integration, webhooks
- **Best Practices**: Implement tiered rate limiting based on usage, use user/company grouping for B2B, set up alerts for unusual usage
- **Performance**: <10ms middleware latency, async event reporting

**Amberflo**:
- **Technology**: Real-time usage metering and billing platform
- **Key Features**: Real-time metering, prepaid/postpaid billing, tiered pricing, usage alerts, cost allocation
- **Use When**: Need sophisticated usage-based pricing, prepaid billing models, real-time usage visibility, cost allocation across teams
- **Pricing**: Free: 1M meter events/month; paid pricing on request
- **Integration**: REST API, SDKs, Stripe integration, webhook notifications
- **Best Practices**: Define meters with appropriate aggregation periods, implement usage buffering for reliability, use customer portal for self-service
- **Performance**: Sub-second metering latency, real-time usage dashboards

**Rationale**: Three options balance simplicity and features:
- Stripe Metering: Simple, Stripe-native, tight billing integration
- Moesif: API analytics + metering, API monetization focus
- Amberflo: Sophisticated pricing, prepaid models, real-time

**Alternatives Considered**: Lago (rejected - open-source but immature), M3ter (rejected - enterprise only)

### 2.6 Secrets Management (New Category - 3 Options)

**Decision**: Infisical, Doppler, AWS Secrets Manager

**Infisical**:
- **Technology**: Open-source secrets management platform
- **Key Features**: Secrets versioning, access control, audit logs, secret rotation, CLI + SDKs, self-hosted or cloud
- **Use When**: Want open-source, prefer self-hosting, need fine-grained access control, cost-sensitive
- **Pricing**: Free (self-hosted); cloud from $18/month per user
- **Integration**: CLI, SDKs (Node.js, Python), GitHub Actions integration, Kubernetes operator
- **Best Practices**: Use environments for staging/production, implement secret rotation policies, leverage service tokens for CI/CD
- **Security**: End-to-end encryption, zero-knowledge architecture, SOC 2 Type II compliant (cloud)

**Doppler**:
- **Technology**: Secrets management for modern development workflows
- **Key Features**: Universal secrets sync, dynamic secrets, access controls, audit logs, integrations with 50+ platforms
- **Use When**: Need multi-platform sync (AWS, GCP, Vercel, GitHub, etc.), want simple UX, require dynamic secrets
- **Pricing**: Free: 5 users, 1 project; team from $12/user/month
- **Integration**: CLI, SDKs, native integrations (Vercel, GitHub Actions, AWS, GCP, Docker, etc.)
- **Best Practices**: Use personal configs for local development, sync to cloud platforms automatically, implement just-in-time access
- **Security**: AES-256 encryption at rest, TLS in transit, SOC 2 Type II compliant

**AWS Secrets Manager**:
- **Technology**: AWS-native secrets storage with automatic rotation
- **Key Features**: Automatic secret rotation, tight AWS integration, encryption with KMS, fine-grained IAM access control
- **Use When**: Deep AWS integration, need automatic rotation (RDS, Redshift), enterprise compliance requirements
- **Pricing**: $0.40 per secret per month + $0.05 per 10K API calls
- **Integration**: AWS SDK, automatic rotation for AWS services (RDS, DocumentDB), Lambda rotation functions
- **Best Practices**: Use resource policies for cross-account access, enable rotation for database credentials, tag secrets for cost allocation
- **Security**: Encrypted with AWS KMS, audit via CloudTrail, VPC endpoint support

**Rationale**: Three options cover different deployment scenarios:
- Infisical: Open-source, self-hosted, cost-effective
- Doppler: Multi-platform sync, best UX, broad integrations
- AWS Secrets Manager: AWS-native, automatic rotation, enterprise

**Alternatives Considered**: HashiCorp Vault (rejected - operational complexity), Azure Key Vault (rejected - Azure lock-in)

### 2.7 Enhanced Error Tracking (Category Enhancement - 3 Options)

**Decision**: Maintain Sentry (enhanced config) and add Rollbar, BugSnag as alternatives

**Sentry (Enhanced)**:
- **Technology**: Leading application monitoring and error tracking
- **Key Features**: Error tracking, performance monitoring, session replay, release health, breadcrumbs, source maps
- **Use When**: Need comprehensive error tracking + performance, want session replay, release tracking critical
- **Pricing**: Free: 5K errors, 10K performance units/month; team from $26/month
- **Integration**: SDKs for all platforms, source map upload, release tracking, integrations (Slack, Jira, GitHub)
- **Best Practices**: Tag releases, use breadcrumbs for context, configure sampling rates, filter sensitive data
- **Performance**: <5ms SDK overhead, async error reporting

**Rollbar**:
- **Technology**: Error tracking and debugging platform
- **Key Features**: Real-time error alerts, intelligent grouping, deploy tracking, telemetry, RQL query language
- **Use When**: Need advanced error grouping, real-time alerts critical, want RQL for custom queries, Sentry alternative
- **Pricing**: Free: 5K events/month; from $15/month for 25K events
- **Integration**: SDKs for 25+ languages, source map support, Slack/PagerDuty/Jira integration
- **Best Practices**: Configure grouping rules, use fingerprinting for deduplication, set up deploy tracking, leverage RQL for insights
- **Performance**: <5ms SDK overhead, real-time alerting

**BugSnag**:
- **Technology**: Error monitoring with focus on mobile and JavaScript
- **Key Features**: Stability monitoring, release health, error diagnostics, user impact analysis, breadcrumbs
- **Use When**: Mobile-first applications, need stability scoring, want user impact metrics, React Native support important
- **Pricing**: Free: 7.5K errors/month; from $59/month for 50K errors
- **Integration**: SDKs for web, mobile, backend; React Native, Expo support; source map upload
- **Best Practices**: Track custom metadata, implement breadcrumbs, monitor stability scores, configure release stages
- **Performance**: <5ms SDK overhead, minimal battery impact on mobile

**Rationale**: Enhanced Sentry configuration as primary option with two solid alternatives:
- Sentry (Enhanced): Most comprehensive, session replay, performance monitoring
- Rollbar: Advanced grouping, RQL queries, real-time alerts
- BugSnag: Mobile-focused, stability monitoring, React Native support

**Alternatives Considered**: Airbrake (rejected - less modern), Raygun (rejected - smaller ecosystem)

## Category 3: Configuration Builder Implementation

### 3.1 Web UI Technology Stack

**Decision**: React 19.2 + Vite + React Flow (for architecture diagrams)

**React 19.2**:
- Latest stable React with improved performance and concurrent features
- TypeScript for type safety
- React Router for navigation between config stages

**Vite**:
- Fast development server with HMR
- Optimized production builds
- TypeScript support out-of-the-box
- Plugin ecosystem for YAML/JSON handling

**React Flow**:
- Visual graph library for architecture diagrams
- Customizable nodes and edges for service representations
- Export to PNG/SVG for documentation
- Interactive with zoom/pan/selection

**State Management**:
- Zustand for global configuration state
- React Query for API calls (compatibility validation, cost estimation)
- Local storage for draft configurations

**UI Framework**:
- shadcn/ui (Radix UI primitives) for accessible components
- Tailwind CSS for styling
- Framer Motion for animations

**Alternatives Considered**:
- Next.js (rejected - unnecessary SSR overhead for config tool)
- Vue (rejected - prefer React alignment with Riso ecosystem)
- D3.js for diagrams (rejected - React Flow more suitable)

### 3.2 CLI TUI Technology Stack

**Decision**: Ink (React for CLIs) + Zustand for state

**Ink**:
- React-based TUI framework
- Component reuse from web UI (business logic)
- Terminal-friendly components (boxes, tables, spinners)
- Cross-platform compatibility

**Features**:
- Interactive prompts with arrow navigation
- Real-time compatibility validation
- Cost estimation display in terminal
- ASCII architecture diagram generation
- Export to copier-answers.yml

**Alternatives Considered**:
- Inquirer (rejected - less powerful)
- blessed (rejected - lower-level)
- yargs + ora (rejected - not component-based)

### 3.3 Compatibility Validation Engine

**Decision**: Rule-based validation with explicit compatibility matrix

**Architecture**:
```typescript
interface CompatibilityRule {
  condition: (selections: Selections) => boolean;
  severity: 'error' | 'warning' | 'info';
  message: string;
  suggestions: string[];
}
```

**Rule Categories**:
1. **Platform Incompatibilities**: Cloudflare Workers + traditional database connection
2. **Service Dependencies**: Supabase Auth requires Supabase Database
3. **Feature Conflicts**: Schema-per-tenant + Cloudflare D1 (no schema support)
4. **Performance Warnings**: Too many services for edge deployment
5. **Cost Warnings**: Expensive combination selected

**Validation Strategy**:
- Evaluate rules on every selection change
- Display errors immediately (block generation)
- Show warnings with ability to proceed
- Provide suggestions for invalid combinations

**Alternatives Considered**:
- AI-based validation (rejected - unpredictable)
- Constraint satisfaction solver (rejected - overkill)

### 3.4 Cost Estimation Engine

**Decision**: Rule-based calculator with per-service pricing tiers

**Pricing Database**:
```typescript
interface ServicePricing {
  service: string;
  tiers: {
    free: { limits: {}, cost: 0 };
    paid: { limits: {}, baseCost: number, variableCost: number[] };
  };
  scalingFactors: (userCount: number) => number;
}
```

**Estimation Scales**:
- 1,000 users (startup/MVP)
- 10,000 users (growth stage)
- 100,000 users (scale stage)

**Cost Components**:
- Base service costs (monthly subscriptions)
- Usage-based costs (API calls, storage, bandwidth)
- Scaling multipliers based on user count
- Hidden costs (egress fees, support contracts)

**Output Format**:
- Total monthly cost estimate with breakdown
- Per-service cost allocation
- Cost comparison between alternative stacks
- Recommendations for cost optimization

**Alternatives Considered**:
- Real-time pricing API (rejected - APIs not available/stable)
- Machine learning model (rejected - insufficient training data)

## Category 4: Migration Tool Architecture

### 4.1 Migration Tool Design

**Decision**: Three-phase architecture (Analyze → Plan → Execute) with rollback capability

**Phase 1: Analysis**
- Parse project files to detect current stack
- Identify all integration points (code, config, environment variables)
- Detect custom modifications beyond template
- Generate dependency graph

**Phase 2: Planning**
- Generate transformation plan for selected migration
- Calculate code diffs for all affected files
- Identify schema changes (database migrations)
- Validate new technology compatibility
- Estimate migration complexity and risk

**Phase 3: Execution**
- Create backup/snapshot before changes
- Apply code transformations (file edits, additions, deletions)
- Execute database migrations if needed
- Update environment variable documentation
- Run test suite to validate migration
- Generate post-migration report

**Rollback Capability**:
- Restore from backup on failure
- Maintain migration history log
- Support partial rollback (per-file)

**Technology Stack**:
- **Python 3.11+** for migration engine (consistency with template layer)
- **AST parsing** for code analysis (avoid regex-based)
- **Jinja2** for template transformations
- **Tree-sitter** for multi-language parsing
- **git** for backup/restore (create migration branches)

**Alternatives Considered**:
- TypeScript migration tool (rejected - Python better for text processing)
- CodeMods (rejected - language-specific, not general)
- Manual migration guides (rejected - error-prone, time-consuming)

### 4.2 Migration Patterns

**Supported Migration Types**:

1. **Authentication Provider Swap** (e.g., Clerk → WorkOS)
   - Replace auth SDK imports
   - Update middleware authentication logic
   - Transform user session handling
   - Update environment variables
   - Migrate user data (if needed)

2. **Database Provider Swap** (e.g., Neon → PlanetScale)
   - Update connection string format
   - Adjust ORM configuration (Prisma/Drizzle)
   - Handle database-specific features (Postgres → MySQL)
   - Export/import schema and data
   - Update backup/restore procedures

3. **Storage Provider Swap** (e.g., R2 → S3)
   - Replace SDK imports
   - Update configuration (buckets, regions)
   - Transform upload/download logic
   - Migrate existing files (optional)
   - Update CDN configuration

4. **Search Provider Swap** (e.g., Algolia → Meilisearch)
   - Replace search SDK
   - Transform indexing logic
   - Update search queries
   - Rebuild search indices
   - Update UI components

**Three-Way Merge Strategy**:
- **Base**: Original template
- **Theirs**: User modifications
- **Ours**: New template (after technology swap)
- Merge result: Preserves user modifications + applies new technology

## Category 5: Multi-Tenant Architecture Patterns

### 5.1 Isolation Levels Research

**Decision**: Support three proven isolation patterns with clear use cases

**Row-Level Security (RLS)**:
- **Implementation**: PostgreSQL RLS policies + tenant_id column
- **Pros**: Simple to implement, cost-effective, good for moderate scale (<10K tenants)
- **Cons**: All tenants share same schema, risk of isolation bugs, limited customization per tenant
- **Use When**: <10K tenants, uniform feature set, PostgreSQL database, cost optimization critical
- **Performance**: Minimal overhead (<5%) with proper indexing
- **Security**: Database-level enforcement, no application bugs can break isolation

**Schema-Per-Tenant**:
- **Implementation**: Separate PostgreSQL schema per tenant, dynamic connection routing
- **Pros**: Better isolation than RLS, per-tenant schema customization, moderate complexity
- **Cons**: Schema limit (typically 10K per database), migrations more complex
- **Use When**: 100-10K tenants, need per-tenant customization, B2B SaaS with varying needs
- **Performance**: Minimal overhead, connection routing adds <5ms
- **Security**: Strong isolation, schema-level access control

**Database-Per-Tenant**:
- **Implementation**: Separate database instance per tenant, connection pool per tenant
- **Pros**: Strongest isolation, complete customization, regulatory compliance, easy backups
- **Cons**: Highest complexity and cost, connection pool management, harder to run queries across tenants
- **Use When**: <1K enterprise tenants, regulatory requirements, maximum customization, backup/restore critical
- **Performance**: No shared resource contention, horizontal scaling
- **Security**: Complete isolation, no cross-tenant data leakage possible

**Implementation Details**:
- Tenant context middleware (extract from subdomain/header/JWT)
- Tenant-scoped queries (automatic tenant_id injection)
- Tenant provisioning workflows (schema/database creation)
- Tenant migration tooling (apply schema changes to all tenants)

**Alternatives Considered**:
- Sharding by tenant (rejected - premature optimization)
- Application-level filtering only (rejected - security risk)

### 5.2 Multi-Tenant Billing Integration

**Decision**: Per-tenant usage tracking with aggregate billing

**Architecture**:
- Usage metering per tenant (API calls, storage, compute)
- Aggregate to subscription level (organization can have multiple tenants)
- Tiered pricing based on tenant count or aggregate usage
- Usage dashboards per tenant
- Admin view of all tenant usage

**Integration Points**:
- Stripe subscription per organization
- Usage metering API reports per-tenant metrics
- Invoice line items show per-tenant breakdowns
- Quota enforcement at tenant level
- Overage handling (block/throttle or allow with charges)

## Category 6: Production Deployment Patterns

### 6.1 Multi-Region Deployment

**Decision**: Active-active multi-region with DNS failover

**Architecture**:
- Deploy application to 3+ regions (US-East, US-West, EU, Asia-Pacific)
- Global load balancer with health checks (Cloudflare/Vercel)
- Database read replicas in each region
- Eventual consistency for multi-region writes
- CDN for static assets (automatic multi-region)

**Failover Strategy**:
- DNS-based with health check endpoints
- Automatic region failover <60 seconds
- Health checks every 10 seconds
- Failback to recovered region (manual or automatic)

**Implementation**:
- Terraform/Pulumi for infrastructure as code
- Vercel: Deploy to multiple regions, configure edge network
- Cloudflare: Deploy Workers to all regions, configure health checks

**Alternatives Considered**:
- Active-passive (rejected - wastes resources)
- Client-side region selection (rejected - poor UX)

### 6.2 Blue-Green Deployment

**Decision**: Zero-downtime deployment with gradual traffic shifting

**Architecture**:
- Blue environment: Current production
- Green environment: New version deployment
- Gradual traffic shift: 1% → 10% → 50% → 100%
- Health checks at each stage
- Automatic rollback on health check failures or error rate spikes

**Implementation**:
- Vercel: Preview deployments + promote to production
- Cloudflare: Gradual rollout feature in Workers
- Custom: Feature flag to control traffic percentage

**Rollback Triggers**:
- Health check failures (>5% failed requests)
- Error rate spike (>2x baseline)
- Manual rollback command
- Timeout without health check success (10 minutes)

**Alternatives Considered**:
- Canary deployment (rejected - similar to gradual rollout, unnecessary distinction)
- Rolling deployment (rejected - partial downtime)

### 6.3 Disaster Recovery

**Decision**: Automated backups with documented RTO/RPO procedures

**Backup Strategy**:
- Database: Automated daily backups + continuous WAL archiving
- Object storage: Versioning enabled + lifecycle policies
- Configurations: Version controlled in git
- Secrets: Backed up to encrypted storage

**Recovery Objectives**:
- RTO (Recovery Time Objective): <1 hour
- RPO (Recovery Point Objective): <15 minutes

**Recovery Procedures**:
1. Identify failure scope (database, application, region)
2. Determine recovery approach (restore from backup, failover to region)
3. Execute recovery runbook
4. Validate data integrity
5. Resume operations
6. Post-mortem analysis

**Testing**:
- Monthly disaster recovery drills
- Automated backup verification
- Restore time measurement

## Category 7: Enhanced Developer Tools

### 7.1 Unified Dev Dashboard

**Decision**: Web-based dashboard with real-time service monitoring

**Features**:
- Real-time service health status (database, cache, auth, jobs, etc.)
- Log aggregation from all services
- Performance metrics (latency, throughput)
- Quick actions (restart service, clear cache, run migrations)
- Environment variable validation

**Technology Stack**:
- React + Vite for dashboard UI
- WebSocket for real-time updates
- Node.js backend for aggregation
- Docker health checks for service status

**Alternatives Considered**:
- Terminal-based dashboard (rejected - limited UI)
- Existing tools like Grafana (rejected - too complex for local dev)

### 7.2 One-Command Setup

**Decision**: Shell script orchestrating all setup steps

**Sequence**:
1. Validate prerequisites (Node.js, pnpm, Docker, database)
2. Install dependencies (pnpm install)
3. Start local services (docker-compose up)
4. Wait for service health (poll health endpoints)
5. Run database migrations
6. Seed fixtures
7. Validate environment variables
8. Start development server
9. Open browser to dashboard

**Error Handling**:
- Clear error messages for missing prerequisites
- Retry logic for transient failures
- Cleanup on fatal errors
- Resume capability (skip completed steps)

**Target Time**: <5 minutes for complete setup

### 7.3 Offline Development Mode

**Decision**: Service mocking with realistic responses

**Mock Implementations**:
- **Authentication**: JWT signing with local key, mock user database
- **Billing**: Simulated subscription states, mock webhook events
- **AI**: Canned responses or local LLM (Ollama)
- **Email**: Log to console, save to local file
- **Storage**: Local filesystem mapping
- **Search**: In-memory index with SQLite FTS
- **Cache**: In-memory cache

**Enabling Offline Mode**:
```bash
pnpm dev --offline
# or
OFFLINE_MODE=true pnpm dev
```

**Alternatives Considered**:
- Recording/replaying API responses (rejected - requires initial recording)
- No offline mode (rejected - poor developer experience)

## Research Conclusions

All technology decisions are made based on:
1. **Clear use cases**: Each option serves distinct needs
2. **Production-ready**: All technologies are proven in production
3. **Active maintenance**: All projects are actively maintained
4. **Good documentation**: All have comprehensive docs
5. **Community support**: Large communities or commercial support available

**Next Phase**: Use these research findings to create data models and contracts in Phase 1.
