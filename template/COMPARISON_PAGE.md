# Feature Comparison Page

The Riso SaaS template includes a production-ready feature comparison page that highlights how Riso compares to competitors like ShipFast, Supastarter, and Makerkit.

## Overview

The comparison page is automatically generated when you create a new SaaS project with `saas_infra_module == "enabled"`. It provides:

1. **Transparent Feature Comparison** - Side-by-side comparison table showing pricing, frameworks, auth providers, payment systems, and more
2. **Unique Advantages** - Highlights what sets Riso apart (Copier modularity, Python + Node.js support, compliance modules, etc.)
3. **Project Configuration Display** - Shows the specific technology choices for the current project
4. **FAQ Section** - Answers common questions about Riso vs. alternatives
5. **Community Links** - Directs users to documentation, GitHub, and Discord

## File Locations

### Next.js Version
- **Page Route**: `/Users/ww/dev/projects/riso/template/files/node/saas/runtime/nextjs/app/(marketing)/comparison/page.tsx.jinja`
- **Layout**: `/Users/ww/dev/projects/riso/template/files/node/saas/runtime/nextjs/app/(marketing)/comparison/layout.tsx.jinja`
- **URL**: `http://your-app.com/comparison`

### Remix Version
- **Route Handler**: `/Users/ww/dev/projects/riso/template/files/node/saas/runtime/remix/app/routes/comparison.tsx.jinja`
- **URL**: `http://your-app.com/comparison`

## Features

### 1. Hero Section
- Clear title: "How Riso Compares"
- Subtitle about transparent feature comparison
- Gradient background with professional styling

### 2. Quick Stats Cards
Shows at a glance:
- **Free/OSS** pricing
- **2+** runtime options
- **8+** auth providers
- **Self-hosting** capability

### 3. Comprehensive Comparison Table
Compares Riso against 3 major competitors:

| Feature | Riso | ShipFast | Supastarter | Makerkit |
|---------|------|----------|-------------|----------|
| **Price** | Free/OSS | $199 | $299 | $299-$599 |
| **Frameworks** | Next.js, Remix, Custom | Next.js | Next.js, Nuxt, SvelteKit | Next.js, Remix |
| **Auth Providers** | Auth.js, Clerk, Better Auth | Auth.js | Auth.js, Clerk | Auth.js, Clerk |
| **Payment Providers** | Stripe, Paddle, LemonSqueezy | Stripe | Stripe, LS | Stripe, Paddle |
| **ORM Options** | Prisma, Drizzle | Prisma | Prisma | Prisma |
| **Multi-tenancy** | ✅ Enterprise-grade | ❌ | ✅ Basic | ✅ |
| **AI Integration** | ✅ RAG-ready with MCP | ❌ | ❌ | ⚠️ Basic |
| **Self-hosting** | ✅ Docker-first | ❌ Limited | ❌ Limited | ❌ Limited |
| **Template System** | Copier (modular) | Clone | Clone | Clone |
| **Compliance Tools** | ✅ GDPR, HIPAA, SOC2 | ❌ | ❌ | ❌ |

### 4. Unique Advantages Section
Highlights 6 key differentiators:

1. **Copier-Based Modularity** - Configure exactly what you need, add/remove features post-generation
2. **Python + Node.js Dual Support** - Not just Next.js or Remix, full Python FastAPI support
3. **Enterprise Compliance Built-in** - GDPR, HIPAA, SOC2 modules included
4. **MCP Server Scaffolding** - AI agent integration ready with FastMCP
5. **Self-Hosting First-Class** - Docker, Kubernetes, VPS ready with zero vendor lock-in
6. **Open Source Community** - Transparent development, no licensing restrictions

### 5. Your Project Configuration
Displays the current project's technology stack:
- Runtime (Next.js 16 or Remix 2.x)
- Hosting (Vercel or Cloudflare)
- Database (Neon or Supabase)
- ORM (Prisma or Drizzle)
- Authentication (Clerk or Auth.js)
- Payments (Stripe, Paddle, or LemonSqueezy)
- Email (Resend or Postmark)
- Analytics (PostHog or Amplitude)
- AI Provider (OpenAI or Anthropic)
- Tenancy Model (B2B Teams or B2C Users)
- RBAC System (Basic Roles or Custom Permissions)

Uses Jinja2 templating to customize based on user selections.

### 6. Frequently Asked Questions
Answers to common questions:
- Why is Riso free?
- Is Riso production-ready?
- What about vendor lock-in?
- How does Riso compare to building from scratch?
- Can I switch runtimes or frameworks later?

### 7. Call-to-Action Section
Links to:
- **View Documentation** - Internal docs link
- **GitHub Repository** - Official Riso GitHub
- **GitHub Discussions** - Community Q&A
- **Discord Community** - Real-time chat

## Jinja2 Template Variables

The page uses Jinja2 templating to customize content based on the SaaS template configuration:

```jinja
{% if saas_infra_module == "enabled" and saas_runtime == "nextjs-16" %}
  <!-- Next.js-specific content -->
{% endif %}

{% if saas_infra_module == "enabled" and saas_runtime == "remix-2" %}
  <!-- Remix-specific content -->
{% endif %}

<!-- Display configured values -->
{{ saas_hosting | title }}      <!-- Vercel, Cloudflare -->
{{ saas_database | title }}     <!-- Neon, Supabase -->
{{ saas_orm | title }}          <!-- Prisma, Drizzle -->
{{ saas_auth_provider | title }}         <!-- Clerk, Authjs -->
{{ saas_billing_provider | title }}      <!-- Stripe, Paddle, Lemonsqueezy -->
{{ saas_email | title }}        <!-- Resend, Postmark -->
{{ saas_analytics | title }}    <!-- Posthog, Amplitude -->
{{ saas_ai | title }}           <!-- Openai, Anthropic -->

{% if saas_tenancy_model == "b2b-teams" %}
  <!-- B2B Teams specific content -->
{% elif saas_tenancy_model == "b2c-users" %}
  <!-- B2C Users specific content -->
{% endif %}

{% if saas_rbac_system == "custom-permissions" %}
  <!-- Custom Permissions specific content -->
{% else %}
  <!-- Basic Roles specific content -->
{% endif %}
```

## Styling

The page uses:
- **Tailwind CSS** for responsive design
- **Lucide React** icons (CheckCircle2, Circle, ArrowRight)
- **CSS Grid** for responsive layouts
- **Dark/light mode ready** with slate color palette
- **Interactive elements** like expandable FAQ items

## Generated Output

When a user creates a Riso SaaS project with `saas_infra_module == "enabled"`, they automatically get:

1. A fully functional comparison page at `/comparison`
2. Proper SEO metadata (title, description, OG tags)
3. Mobile-responsive design (grid columns adjust from 1 → 2 → 4)
4. Accessibility features (semantic HTML, proper heading hierarchy)
5. Interactive FAQ with CSS-based expand/collapse
6. Customized content showing their exact technology stack

## Customization

Users can customize the comparison page by:

1. **Editing the data structure** - Update the `competitors` object with different competitors
2. **Adding features** - Extend the `featureCategories` array
3. **Styling** - Modify Tailwind classes for different colors/layouts
4. **Content** - Update FAQ questions, advantages, or descriptive text

## Best Practices

1. **Keep competitor data accurate** - Update as competitors' offerings change
2. **Highlight genuine advantages** - Don't make false claims
3. **Link to proof** - Back up claims with documentation/links
4. **Test responsiveness** - Ensure the comparison table is readable on mobile
5. **Update regularly** - Keep pricing and features current
6. **A/B test CTA** - Try different button text and colors

## Integration

The comparison page integrates seamlessly with:
- **Marketing layout** - Uses standard (marketing) group layout
- **Navigation** - Can be added to main nav via update to header component
- **SEO** - Proper metadata for search engines and social sharing
- **Analytics** - Can track button clicks and page engagement

## Future Enhancements

Potential improvements:
1. **Interactive feature toggling** - Let users select which features matter to them
2. **Live pricing API** - Fetch competitor pricing from external source
3. **Community reviews** - Embed ratings from ProductHunt or G2
4. **ROI calculator** - Show time/cost savings using Riso
5. **Customer testimonials** - Include quotes from Riso users
6. **Feature request voting** - Let community vote on missing features
