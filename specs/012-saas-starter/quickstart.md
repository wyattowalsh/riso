# Quickstart Guide: SaaS Starter Template

**Feature**: 012-saas-starter  
**Audience**: Developers using the generated SaaS application  
**Time to Complete**: 15-30 minutes

## Overview

This quickstart guide walks you through generating a production-ready SaaS application using the Riso SaaS Starter module, setting up your development environment, and deploying to production.

**What you'll build**: A full-stack SaaS application with authentication, billing, database, background jobs, email sending, analytics, AI integration, file storage, and comprehensive observability.

**Time from start to deployed application**: ~30 minutes

---

## Prerequisites

Before you begin, ensure you have:

- **Node.js 20 LTS** - [Install from nodejs.org](https://nodejs.org/)
- **pnpm ≥8** - `npm install -g pnpm`
- **Copier ≥9.0** - `pip install copier` or `pipx install copier`
- **Git** - For version control
- **Accounts** for your chosen services (see Step 3)

Check versions:
```bash
node --version  # Should be v20.x.x
pnpm --version  # Should be ≥8.0.0
copier --version  # Should be ≥9.0.0
```

---

## Step 1: Generate Your SaaS Application

### Option A: Generate from Riso Template

```bash
# Clone or download the Riso template
copier copy gh:wyattowalsh/riso my-saas-app

# Navigate to project
cd my-saas-app
```

During the Copier prompts:

1. **Enable SaaS Starter Module**
   ```
   Enable SaaS Starter module? [disabled]
   > enabled
   ```

2. **Choose Your Runtime**
   ```
   Select runtime framework: [nextjs-16]
   - nextjs-16: React 19.2, App Router, Turbopack, Vercel-first
   - remix-2: Server-first routes, explicit data loading
   > nextjs-16
   ```

3. **Select Infrastructure** (14 categories total)
   - Hosting: `vercel` or `cloudflare`
   - Database: `neon` or `supabase`
   - ORM: `prisma` or `drizzle`
   - Auth: `clerk` or `authjs`
   - Enterprise Bridge: `workos` or `none`
   - Billing: `stripe` or `paddle`
   - Jobs: `triggerdev` or `inngest`
   - Email: `resend` or `postmark`
   - Analytics: `posthog` or `amplitude`
   - AI: `openai` or `anthropic`
   - Storage: `r2` or `supabase-storage`
   - CI/CD: `github-actions` or `cloudflare-ci`

4. **Configure Observability**
   ```
   Enable Sentry for error tracking? [true]
   Enable Datadog for APM? [true]
   Enable OpenTelemetry? [true]
   Enable structured logging? [true]
   ```

5. **Additional Options**
   ```
   Include seeded fixtures? [true]
   Include test data factories? [true]
   Test suite level: [standard]
   - standard: Unit + integration tests
   - comprehensive: Standard + E2E tests
   ```

### Option B: Use a Recommended Stack

Skip individual choices and use a pre-configured stack:

```bash
# Vercel Starter Stack (fastest setup, best DX)
copier copy --data saas_preset=vercel-starter gh:wyattowalsh/riso my-saas-app

# Edge-Optimized Stack (global edge, low cost)
copier copy --data saas_preset=edge-optimized gh:wyattowalsh/riso my-saas-app

# All-in-One Platform Stack (Supabase + Vercel)
copier copy --data saas_preset=all-in-one-platform gh:wyattowalsh/riso my-saas-app

# Enterprise-Ready Stack (SSO, SCIM, compliance)
copier copy --data saas_preset=enterprise-ready gh:wyattowalsh/riso my-saas-app
```

---

## Step 2: Review Generated Project

Your project structure:

```
my-saas-app/
├── app/                      # Next.js App Router (or remix routes/)
│   ├── (auth)/               # Auth pages (login, signup)
│   ├── (dashboard)/          # Protected dashboard
│   ├── api/                  # API routes
│   └── middleware.ts         # Auth + tracing middleware
├── lib/                      # Core business logic
│   ├── auth/                 # Authentication helpers
│   ├── billing/              # Billing integration
│   ├── database/             # Database client
│   ├── jobs/                 # Background jobs
│   ├── email/                # Email sending
│   ├── analytics/            # Analytics tracking
│   ├── ai/                   # AI integration
│   ├── storage/              # File storage
│   └── observability/        # Sentry + Datadog + OTel
├── prisma/                   # Database schema + migrations
│   ├── schema.prisma
│   ├── seed.ts               # Seed data fixtures
│   └── migrations/
├── tests/                    # Test suites
│   ├── unit/                 # Unit tests
│   ├── integration/          # Service integration tests
│   └── e2e/                  # End-to-end tests (if comprehensive)
├── .env.example              # Environment variable template
├── saas-starter.config.ts    # Your technology selections
├── package.json              # Dependencies
└── README.md                 # Project-specific README
```

**Key files to review:**
- `saas-starter.config.ts` - Documents your technology choices
- `.env.example` - Lists required environment variables
- `README.md` - Project-specific setup instructions

---

## Step 3: Set Up Service Accounts

Create accounts and obtain API keys for your selected services.

### Authentication (Clerk example)

1. Sign up at [clerk.com](https://clerk.com)
2. Create a new application
3. Copy API keys from dashboard:
   ```
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
   CLERK_SECRET_KEY=sk_test_...
   ```

### Database (Neon example)

1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy connection string:
   ```
   DATABASE_URL=postgres://user:pass@host.neon.tech/db?sslmode=require
   ```

### Billing (Stripe example)

1. Sign up at [stripe.com](https://stripe.com)
2. Get test mode API keys from dashboard
3. Set up webhook endpoint:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### Other Services

Follow similar patterns for:
- **Jobs**: Trigger.dev or Inngest dashboard
- **Email**: Resend or Postmark account
- **Analytics**: PostHog or Amplitude project
- **AI**: OpenAI or Anthropic API keys
- **Storage**: Cloudflare R2 or Supabase bucket
- **Observability**: Sentry project, Datadog account

**See `.env.example` for complete list of required variables.**

---

## Step 4: Configure Environment Variables

Create `.env.local` from template:

```bash
cp .env.example .env.local
```

Edit `.env.local` with your API keys:

```bash
# Database
DATABASE_URL="postgres://user:pass@host.neon.tech/db"

# Auth (Clerk)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_test_..."
CLERK_SECRET_KEY="sk_test_..."

# Billing (Stripe)
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# Email (Resend)
RESEND_API_KEY="re_..."

# Jobs (Trigger.dev)
TRIGGER_API_KEY="trigger_..."

# Analytics (PostHog)
NEXT_PUBLIC_POSTHOG_KEY="phc_..."
NEXT_PUBLIC_POSTHOG_HOST="https://app.posthog.com"

# AI (OpenAI)
OPENAI_API_KEY="sk-..."

# Observability
SENTRY_DSN="https://...@sentry.io/..."
DD_API_KEY="..." # Datadog
```

**Validate configuration:**
```bash
pnpm validate:env
```

This checks that all required variables are set with correct format.

---

## Step 5: Install Dependencies & Initialize Database

```bash
# Install NPM dependencies
pnpm install

# Generate Prisma client (or Drizzle types)
pnpm generate

# Push database schema
pnpm db:push

# Seed database with fixtures (if enabled)
pnpm db:seed

# Verify database connection
pnpm db:studio  # Opens Prisma Studio
```

You should see seed data:
- 10 example users
- 5 example organizations
- Sample subscriptions and usage records

---

## Step 6: Start Development Server

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000)

**You should see:**
- ✅ Landing page
- ✅ Login/signup buttons
- ✅ Working authentication flow
- ✅ Protected dashboard (after login)

**Test the authentication flow:**
1. Click "Sign Up"
2. Create an account
3. Verify email (if configured)
4. Access dashboard

---

## Step 7: Verify Service Integrations

### Test Authentication
```bash
# Visit http://localhost:3000
# Click "Sign Up" → Create account → Should redirect to dashboard
```

### Test Billing
```bash
# In dashboard, click "Upgrade Plan"
# Use Stripe test card: 4242 4242 4242 4242
# Should create subscription successfully
```

### Test Background Jobs
```bash
# Trigger welcome email job
pnpm run:job send-welcome-email --userId <user-id>

# Check job status in Trigger.dev dashboard
```

### Test Email Sending
```bash
# Send test email
pnpm email:test --to your@email.com

# Check inbox for email
```

### Test Analytics
```bash
# Visit dashboard → should see event tracked in PostHog
# Event: page_view, user_id: <your-user-id>
```

### Test AI Integration
```bash
# Visit /api/ai/chat endpoint
# Send message → should get AI response
```

### Test File Upload
```bash
# Upload file in dashboard
# Should appear in R2 or Supabase Storage
```

### Test Observability
```bash
# Trigger an error intentionally
# Check Sentry dashboard for error report
# Check Datadog for APM trace
```

---

## Step 8: Run Test Suite

```bash
# Run all tests
pnpm test

# Run specific test suites
pnpm test:unit          # Unit tests
pnpm test:integration   # Integration tests (requires services)
pnpm test:e2e           # End-to-end tests (if comprehensive)

# Run with coverage
pnpm test:coverage

# Watch mode (for development)
pnpm test:watch
```

**Expected results:**
- ✅ Unit tests: 100+ tests passing
- ✅ Integration tests: All service connections verified
- ✅ E2E tests: Critical user flows validated
- ✅ Coverage: >70% (standard) or >95% (strict)

---

## Step 9: Deploy to Production

### Option A: Deploy to Vercel

```bash
# Install Vercel CLI
pnpm install -g vercel

# Login
vercel login

# Deploy
vercel

# Add environment variables
vercel env add DATABASE_URL
vercel env add CLERK_SECRET_KEY
# ... (add all variables from .env.local)

# Deploy to production
vercel --prod
```

### Option B: Deploy to Cloudflare

```bash
# Install Wrangler CLI
pnpm install -g wrangler

# Login
wrangler login

# Add secrets
wrangler secret put DATABASE_URL
wrangler secret put CLERK_SECRET_KEY
# ... (add all secrets)

# Deploy
wrangler deploy
```

### Post-Deployment Checklist

- [ ] Set production environment variables
- [ ] Run database migrations (`pnpm db:migrate:deploy`)
- [ ] Configure webhook URLs (Stripe, Clerk, etc.)
- [ ] Set up custom domain
- [ ] Enable monitoring alerts (Sentry, Datadog)
- [ ] Test production deployment end-to-end
- [ ] Set up backups (database, storage)

---

## Step 10: Configure Webhooks

Many services require webhook endpoints for real-time events.

### Stripe Webhooks

1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://your-domain.com/api/webhooks/stripe`
3. Select events:
   - `invoice.paid`
   - `invoice.payment_failed`
   - `subscription.created`
   - `subscription.updated`
   - `subscription.deleted`
4. Copy webhook secret to `.env`:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### Clerk Webhooks

1. Go to Clerk Dashboard → Webhooks
2. Add endpoint: `https://your-domain.com/api/webhooks/clerk`
3. Select events:
   - `user.created`
   - `user.updated`
   - `session.created`
4. Copy signing secret

### Trigger.dev / Inngest

Jobs services automatically configure webhooks during setup.

---

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
pnpm db:test-connection

# Common fixes:
# 1. Check DATABASE_URL format
# 2. Ensure database is accessible (firewall rules)
# 3. Verify SSL mode (Neon requires ?sslmode=require)
```

### Auth Not Working

```bash
# Verify Clerk/Auth.js configuration
pnpm validate:auth

# Check:
# 1. API keys are correct
# 2. Middleware is configured
# 3. Auth provider dashboard shows requests
```

### Observability Not Showing Data

```bash
# Verify Sentry DSN
pnpm test:sentry

# Check:
# 1. DSN is correct format
# 2. Source maps are uploaded (for production)
# 3. Error rate limits not exceeded
```

### Jobs Not Running

```bash
# Check job queue connection
pnpm jobs:status

# Trigger test job manually
pnpm run:job test-job

# Check:
# 1. API keys are correct
# 2. Job service dashboard shows connection
# 3. No rate limits or quota issues
```

---

## Next Steps

Now that your SaaS application is running:

1. **Customize branding** - Update logo, colors, typography in `app/config.ts`
2. **Add business logic** - Implement your unique features in `lib/`
3. **Create pricing plans** - Define plans in Stripe/Paddle dashboard
4. **Write documentation** - Add guides for your specific features
5. **Set up monitoring** - Configure alerts in Sentry and Datadog
6. **Optimize performance** - Review Datadog APM for bottlenecks
7. **Add tests** - Expand test coverage for your custom features

---

## Learn More

- **Documentation**: See `docs/` directory for detailed guides
- **API Reference**: `docs/api-reference.md`
- **Deployment**: `docs/deployment.md`
- **Security**: `docs/security.md`
- **Troubleshooting**: `docs/troubleshooting.md`

**Technology-Specific Guides:**
- See `docs/integrations/{service}.md` for each integration
- Examples: `docs/integrations/clerk.md`, `docs/integrations/stripe.md`

---

## Performance Benchmarks

**Expected performance** (based on default Vercel Starter stack):

- **Cold start**: ~300ms
- **Request latency (p95)**: ~100ms
- **Time to first byte**: ~50ms
- **Database query time**: ~20-40ms

**Scaling targets:**
- 10,000 concurrent users
- 100,000 requests/day
- <200ms p95 latency

Monitor actual performance in Datadog APM dashboard.

---

## Cost Estimates

**Monthly costs** (at 10,000 active users):

| Service | Cost |
|---------|------|
| Vercel Pro | $20 |
| Neon | $50-100 |
| Clerk | $100-200 |
| Stripe | 2.9% + $0.30/txn |
| Trigger.dev | $50-100 |
| Resend | $20-50 |
| PostHog | $50-100 |
| OpenAI | Variable (usage) |
| Cloudflare R2 | $5-15 |
| Sentry | $26 |
| Datadog | $100-200 |
| **Total** | **$500-1000** |

Costs vary based on:
- Usage volume
- Selected technologies
- Optimization efforts

---

## Support

- **Issues**: [GitHub Issues](https://github.com/wyattowalsh/riso/issues)
- **Discussions**: [GitHub Discussions](https://github.com/wyattowalsh/riso/discussions)
- **Documentation**: [Full Documentation](https://github.com/wyattowalsh/riso)

---

## Conclusion

🎉 **Congratulations!** You've successfully generated and deployed a production-ready SaaS application with authentication, billing, database, background jobs, email, analytics, AI, storage, and observability.

**Time invested**: ~30 minutes  
**Alternative (manual integration)**: 40-80 hours  
**Time saved**: ~40+ hours

Now focus on building your unique product features instead of infrastructure setup!
