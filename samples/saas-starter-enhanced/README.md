# SaaS Starter Enhanced Sample Configurations

This directory contains sample configurations demonstrating the enhanced SaaS starter with expanded technology options.

## Sample Configurations

### 1. Edge-Optimized V2
**File**: `edge-optimized-v2.yml`

Full edge deployment with Cloudflare stack:
- Runtime: Next.js 16
- Hosting: Cloudflare Pages
- Database: Supabase (REST API mode for edge compatibility)
- Auth: Supabase Auth
- Cache: Cloudflare KV
- Storage: Cloudflare R2

**Use case**: Global edge application, minimal latency, cost-optimized

### 2. Enterprise-Ready V2
**File**: `enterprise-ready-v2.yml`

Enterprise B2B SaaS with compliance features:
- Runtime: Next.js 16
- Hosting: Vercel
- Database: CockroachDB (multi-region, compliance)
- Auth: WorkOS (SSO, SCIM)
- Cache: Redis/Upstash
- Search: Algolia
- Feature Flags: LaunchDarkly
- CMS: Contentful
- Secrets: Doppler

**Use case**: Enterprise customers, regulatory compliance, SSO required

### 3. All-In-One V2
**File**: `all-in-one-v2.yml`

Supabase all-in-one platform:
- Runtime: Next.js 16
- Hosting: Vercel
- Database: Supabase
- Auth: Supabase Auth
- Storage: Supabase Storage
- No additional services (integrated platform)

**Use case**: Rapid MVP, unified platform, minimal vendors

### 4. Search-Heavy
**File**: `search-heavy.yml`

Content-rich application with advanced search:
- Runtime: Next.js 16
- Hosting: Vercel
- Database: Neon
- Search: Algolia (with merchandising)
- CMS: Sanity
- Cache: Vercel KV

**Use case**: E-commerce, content platforms, search-first applications

### 5. AI-Powered
**File**: `ai-powered.yml`

AI-first application:
- Runtime: Next.js 16
- AI: OpenAI GPT-4
- Database: Neon
- Cache: Redis (for AI response caching)
- Feature Flags: PostHog (A/B test AI prompts)

**Use case**: AI chat applications, document analysis, AI-powered features

## Using Sample Configurations

Generate a project using a sample configuration:

```bash
copier copy gh:wyattowalsh/riso my-project \\
  --answers-file=samples/saas-starter-enhanced/edge-optimized-v2.yml
```

Or use the configuration builder to import and modify:

```bash
pnpm config:builder --import samples/saas-starter-enhanced/enterprise-ready-v2.yml
```

## Creating Custom Configurations

1. Use the configuration builder (web UI or CLI TUI)
2. Select your technology stack
3. View real-time cost estimates and compatibility validation
4. Export to `copier-answers.yml`
5. Generate your project

## Validation

All sample configurations:
- ✅ Pass compatibility validation (no conflicting technologies)
- ✅ Render successfully without errors
- ✅ Include cost estimates at 1K/10K/100K users
- ✅ Have documented use cases

Last Updated: 2025-11-02
