# SaaS Integrations

This directory contains integration templates for 80+ technology options across 21 infrastructure categories.

## Structure

### Original Categories (Expanded from 2 to 4 options)

- `auth/` - Authentication providers (Clerk, Auth.js, WorkOS, Supabase Auth)
- `database/` - Database providers (Neon, Supabase, PlanetScale, CockroachDB) 
- `orm/` - ORMs (Prisma, Drizzle, Kysely, TypeORM)
- `billing/` - Billing providers (Stripe, Paddle)
- `storage/` - File storage (R2, Supabase Storage, S3, UploadThing)
- `email/` - Email providers (Resend, Postmark, SendGrid, SES)
- `ai/` - AI providers (OpenAI, Anthropic, Gemini, Ollama)
- `analytics/` - Analytics (PostHog, Amplitude)
- `jobs/` - Background jobs (Trigger.dev, Inngest)

### NEW Categories (Spec 017 Enhancement)

- `search/` - Search providers (Algolia, Meilisearch, Typesense)
- `cache/` - Cache providers (Redis/Upstash, Cloudflare KV, Vercel KV)
- `feature-flags/` - Feature flag providers (LaunchDarkly, PostHog, GrowthBook)
- `cms/` - Content management systems (Contentful, Sanity, Payload, Strapi)
- `usage-metering/` - Usage tracking and metering (Stripe Metering, Moesif, Amberflo)
- `secrets/` - Secrets management (Infisical, Doppler, AWS Secrets Manager)
- `error-tracking/` - Error tracking (Sentry, Rollbar, BugSnag)

## Integration Template Pattern

Each integration follows a standard structure:

```
<category>/<provider>/
├── client.ts.jinja              # Service client initialization
├── config.ts.jinja              # Configuration
├── types.ts.jinja               # TypeScript types
├── middleware.ts.jinja          # Middleware/interceptors (if applicable)
├── examples/                    # Usage examples
│   ├── basic.ts.jinja
│   └── advanced.ts.jinja
└── README.md.jinja             # Provider-specific documentation
```

## Conditional Rendering

Integrations use Jinja2 conditionals to only render when selected:

```jinja2
{% if saas_search == 'algolia' %}
// Algolia integration code
{% endif %}
```

## Cross-Category Integration

Many integrations are aware of other selections:

```jinja2
{% if saas_search == 'algolia' and saas_database == 'supabase' %}
// Algolia + Supabase real-time sync
{% endif %}
```

## Status

- **Phase 1-2**: Foundation (Complete)
- **Phase 3**: Expanded original categories (In Progress)
- **Phase 4**: New categories (Planned)

Last Updated: 2025-11-02
