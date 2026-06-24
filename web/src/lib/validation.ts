/**
 * Real-time Configuration Validation for Riso
 *
 * Comprehensive validation system that checks for:
 * - Mutual exclusions (conflicting options)
 * - Dependencies (required options)
 * - Cost warnings (third-party service costs)
 * - Best practices (recommendations)
 *
 * Integrates with DependencyWarnings component for real-time feedback.
 */

import type { RisoConfig } from './store'

export type ValidationSeverity = 'error' | 'warning' | 'info'

export interface ValidationRule {
  id: string
  check: (state: Partial<RisoConfig>) => boolean // true = violation
  message: string
  severity: ValidationSeverity
  affectedFields: (keyof RisoConfig)[]
  quickFix?: {
    label: string
    apply: (state: Partial<RisoConfig>) => Partial<RisoConfig>
  }
  details?: string
}

export interface ValidationResult {
  id: string
  message: string
  severity: ValidationSeverity
  affectedFields: (keyof RisoConfig)[]
  quickFix?: {
    label: string
    apply: (state: Partial<RisoConfig>) => Partial<RisoConfig>
  }
  details?: string
}

export const VALIDATION_RULES: ValidationRule[] = [
  // ========================================
  // MUTUAL EXCLUSIONS
  // ========================================
  {
    id: 'clerk-workos-conflict',
    check: (s) =>
      s.saas_auth_provider === 'clerk' && s.saas_enterprise_bridge === 'workos',
    message: 'Clerk already includes enterprise SSO; WorkOS bridge is redundant',
    severity: 'warning',
    affectedFields: ['saas_auth_provider', 'saas_enterprise_bridge'],
    quickFix: {
      label: 'Remove WorkOS bridge',
      apply: () => ({ saas_enterprise_bridge: 'none' }),
    },
    details:
      'Clerk Pro and Enterprise plans include SAML/SSO support. Consider using WorkOS only if you need advanced enterprise features.',
  },

  {
    id: 'nextjs-cloudflare-conflict',
    check: (s) =>
      s.saas_runtime === 'nextjs-16' && s.saas_hosting === 'cloudflare',
    message: 'Next.js 16 is optimized for Vercel; Cloudflare may have limited support',
    severity: 'warning',
    affectedFields: ['saas_runtime', 'saas_hosting'],
    quickFix: {
      label: 'Use Vercel hosting',
      apply: () => ({ saas_hosting: 'vercel' }),
    },
    details:
      'Next.js features like Server Actions, Parallel Routes, and Suspense work best on Vercel. For Cloudflare, consider Remix.',
  },

  {
    id: 'remix-vercel-conflict',
    check: (s) => s.saas_runtime === 'remix-2' && s.saas_hosting === 'vercel',
    message: 'Remix is optimized for Cloudflare; Vercel may have limited support',
    severity: 'warning',
    affectedFields: ['saas_runtime', 'saas_hosting'],
    quickFix: {
      label: 'Use Cloudflare hosting',
      apply: () => ({ saas_hosting: 'cloudflare' }),
    },
    details:
      'Remix works best on Cloudflare Pages/Workers with edge runtime. For Vercel, consider Next.js.',
  },

  // ========================================
  // DEPENDENCIES (HARD REQUIREMENTS)
  // ========================================
  {
    id: 'billing-requires-auth',
    check: (s) =>
      s.saas_billing_module === 'enabled' && s.saas_auth_module !== 'enabled',
    message: 'Billing features require authentication to be enabled',
    severity: 'error',
    affectedFields: ['saas_billing_module', 'saas_auth_module'],
    quickFix: {
      label: 'Enable Auth layer',
      apply: () => ({ saas_auth_module: 'enabled', saas_auth_provider: 'clerk' }),
    },
    details: 'Billing subscriptions must be tied to authenticated users.',
  },

  {
    id: 'auth-requires-infra',
    check: (s) =>
      s.saas_auth_module === 'enabled' && s.saas_infra_module !== 'enabled',
    message: 'Authentication requires infrastructure layer to be enabled',
    severity: 'error',
    affectedFields: ['saas_auth_module', 'saas_infra_module'],
    quickFix: {
      label: 'Enable Infrastructure',
      apply: () => ({
        saas_infra_module: 'enabled',
        saas_database: 'neon',
        saas_orm: 'prisma',
      }),
    },
    details:
      'Auth providers need a database to store user data and session information.',
  },

  {
    id: 'app-requires-infra',
    check: (s) =>
      s.saas_app_module === 'enabled' && s.saas_infra_module !== 'enabled',
    message: 'Application layer requires infrastructure to be enabled',
    severity: 'error',
    affectedFields: ['saas_app_module', 'saas_infra_module'],
    quickFix: {
      label: 'Enable Infrastructure',
      apply: () => ({
        saas_infra_module: 'enabled',
        saas_database: 'neon',
        saas_orm: 'prisma',
      }),
    },
    details: 'App features like jobs, email, and storage require database infrastructure.',
  },

  {
    id: 'openapi-requires-api',
    check: (s) =>
      s.fumadocs_openapi === 'enabled' && s.api_module !== 'enabled',
    message: 'OpenAPI documentation requires an API module',
    severity: 'error',
    affectedFields: ['fumadocs_openapi', 'api_module'],
    quickFix: {
      label: 'Enable API module',
      apply: () => ({ api_module: 'enabled', api_languages: ['python'] }),
    },
    details: 'OpenAPI docs are generated from API endpoints.',
  },

  {
    id: 'docusaurus-openapi-requires-api',
    check: (s) =>
      s.docusaurus_openapi === 'enabled' && s.api_module !== 'enabled',
    message: 'OpenAPI documentation requires an API module',
    severity: 'error',
    affectedFields: ['docusaurus_openapi', 'api_module'],
    quickFix: {
      label: 'Enable API module',
      apply: () => ({ api_module: 'enabled', api_languages: ['python'] }),
    },
    details: 'OpenAPI docs are generated from API endpoints.',
  },

  {
    id: 'graphql-requires-api',
    check: (s) =>
      (s.api_features === 'graphql' || s.api_features === 'graphql,websocket') &&
      s.api_module !== 'enabled',
    message: 'GraphQL features require an API module',
    severity: 'error',
    affectedFields: ['api_features', 'api_module'],
    quickFix: {
      label: 'Enable API module',
      apply: () => ({ api_module: 'enabled', api_languages: ['python'] }),
    },
  },

  {
    id: 'ai-tools-mcp-requires-module',
    check: (s) =>
      Boolean(
        s.ai_tools_mcp_thinking ||
          s.ai_tools_mcp_web ||
          s.ai_tools_mcp_documents ||
          s.ai_tools_mcp_utilities ||
          s.ai_tools_mcp_search
      ) && s.ai_tools_module !== 'enabled',
    message: 'MCP servers require AI Tools module to be enabled',
    severity: 'error',
    affectedFields: [
      'ai_tools_module',
      'ai_tools_mcp_thinking',
      'ai_tools_mcp_web',
      'ai_tools_mcp_documents',
      'ai_tools_mcp_utilities',
      'ai_tools_mcp_search',
    ],
    quickFix: {
      label: 'Enable AI Tools',
      apply: () => ({ ai_tools_module: 'enabled' }),
    },
  },

  // ========================================
  // COST WARNINGS
  // ========================================
  {
    id: 'stripe-cost-warning',
    check: (s) => s.saas_billing_provider === 'stripe',
    message: 'Stripe charges 2.9% + $0.30 per transaction',
    severity: 'info',
    affectedFields: ['saas_billing_provider'],
    details:
      'Standard pricing. Volume discounts available. Consider Stripe Connect for marketplace features.',
  },

  {
    id: 'paddle-cost-warning',
    check: (s) => s.saas_billing_provider === 'paddle',
    message: 'Paddle charges 5% + $0.50 per transaction',
    severity: 'info',
    affectedFields: ['saas_billing_provider'],
    details:
      'Higher fees but includes tax compliance globally. Good for international SaaS.',
  },

  {
    id: 'lemonsqueezy-cost-warning',
    check: (s) => s.saas_billing_provider === 'lemonsqueezy',
    message: 'Lemon Squeezy charges 5% per transaction',
    severity: 'info',
    affectedFields: ['saas_billing_provider'],
    details:
      'Includes merchant of record service. No monthly fees. Best for small SaaS startups.',
  },

  {
    id: 'clerk-cost-warning',
    check: (s) => s.saas_auth_provider === 'clerk',
    message: 'Clerk is free up to 10,000 monthly active users',
    severity: 'info',
    affectedFields: ['saas_auth_provider'],
    details:
      'After 10k MAU, pricing starts at $25/month per 1000 MAU. Enterprise SSO requires Pro plan.',
  },

  {
    id: 'posthog-cost-warning',
    check: (s) => s.saas_analytics === 'posthog',
    message: 'PostHog offers 1M events/month free, then pay-as-you-go',
    severity: 'info',
    affectedFields: ['saas_analytics'],
    details: 'Includes product analytics, session replay, and feature flags.',
  },

  {
    id: 'amplitude-cost-warning',
    check: (s) => s.saas_analytics === 'amplitude',
    message: 'Amplitude offers 10M events/month free for startups',
    severity: 'info',
    affectedFields: ['saas_analytics'],
    details: 'Growth plan starts at $49/month. Best for product-led growth teams.',
  },

  {
    id: 'neon-cost-warning',
    check: (s) => s.saas_database === 'neon',
    message: 'Neon offers generous free tier with 3GB storage',
    severity: 'info',
    affectedFields: ['saas_database'],
    details:
      'Serverless Postgres. Pay-as-you-go after free tier. Cold starts on free tier.',
  },

  {
    id: 'supabase-cost-warning',
    check: (s) => s.saas_database === 'supabase',
    message: 'Supabase free tier includes 500MB database + 1GB storage',
    severity: 'info',
    affectedFields: ['saas_database'],
    details:
      'Pro plan at $25/month includes 8GB database + 100GB storage. Paused projects on free tier.',
  },

  {
    id: 'algolia-cost-warning',
    check: (s) =>
      s.fumadocs_search_provider === 'algolia' ||
      s.docusaurus_search_provider === 'algolia',
    message: 'Algolia offers 10k search requests/month free',
    severity: 'info',
    affectedFields: ['fumadocs_search_provider', 'docusaurus_search_provider'],
    details:
      'Standard plan starts at $1/1000 requests after free tier. Premium features cost more.',
  },

  {
    id: 'orama-cloud-cost-warning',
    check: (s) => s.fumadocs_search_provider === 'orama-cloud',
    message: 'Orama Cloud offers 100k search operations/month free',
    severity: 'info',
    affectedFields: ['fumadocs_search_provider'],
    details:
      'Pro plan at $49/month. Best for AI-powered semantic search. Self-hosted Orama is free.',
  },

  // ========================================
  // BEST PRACTICES & RECOMMENDATIONS
  // ========================================
  {
    id: 'saas-strict-quality',
    check: (s) =>
      (s.saas_infra_module === 'enabled' ||
        s.saas_auth_module === 'enabled' ||
        s.saas_billing_module === 'enabled') &&
      s.quality_profile === 'standard',
    message: 'Consider strict quality profile for SaaS applications',
    severity: 'info',
    affectedFields: ['quality_profile'],
    quickFix: {
      label: 'Use Strict quality',
      apply: () => ({ quality_profile: 'strict' }),
    },
    details:
      'Strict profile adds comprehensive linting, type checking, and security scanning.',
  },

  {
    id: 'monorepo-shared-logic',
    check: (s) => s.project_layout === 'monorepo' && s.shared_logic === 'disabled',
    message: 'Enable shared logic module for monorepo projects',
    severity: 'info',
    affectedFields: ['shared_logic', 'project_layout'],
    quickFix: {
      label: 'Enable shared logic',
      apply: () => ({ shared_logic: 'enabled' }),
    },
    details:
      'Shared logic package helps organize common utilities, types, and business logic.',
  },

  {
    id: 'api-changelog-recommend',
    check: (s) => s.api_module === 'enabled' && s.changelog_module === 'disabled',
    message: 'Enable changelog for API versioning and release notes',
    severity: 'info',
    affectedFields: ['changelog_module'],
    quickFix: {
      label: 'Enable changelog',
      apply: () => ({ changelog_module: 'enabled' }),
    },
    details:
      'Semantic-release generates changelogs automatically from commit messages.',
  },

  {
    id: 'graphql-python-recommend',
    check: (s) =>
      (s.api_features === 'graphql' || s.api_features === 'graphql,websocket') &&
      !s.api_languages?.includes('python'),
    message: 'Python API recommended for GraphQL (Strawberry framework)',
    severity: 'info',
    affectedFields: ['api_languages'],
    quickFix: {
      label: 'Add Python API',
      apply: (state) => ({ api_languages: [...(state.api_languages || []), 'python'] }),
    },
    details:
      'Strawberry is the most mature GraphQL framework with excellent type safety and async support.',
  },

  {
    id: 'ai-search-orama-recommend',
    check: (s) =>
      s.fumadocs_ai_search === 'enabled' &&
      s.fumadocs_search_provider !== 'orama' &&
      s.fumadocs_search_provider !== 'orama-cloud',
    message: 'Orama search provider recommended for AI-powered search',
    severity: 'info',
    affectedFields: ['fumadocs_search_provider'],
    quickFix: {
      label: 'Use Orama',
      apply: () => ({ fumadocs_search_provider: 'orama' }),
    },
    details: 'Orama provides vector embeddings for semantic search with AI.',
  },

  {
    id: 'typedoc-typescript-recommend',
    check: (s) =>
      s.fumadocs_typedoc === 'enabled' && !s.api_languages?.includes('node'),
    message: 'TypeDoc requires Node.js/TypeScript API',
    severity: 'warning',
    affectedFields: ['fumadocs_typedoc', 'api_languages'],
    quickFix: {
      label: 'Add Node API',
      apply: (state) => ({ api_languages: [...(state.api_languages || []), 'node'] }),
    },
    details: 'TypeDoc generates documentation from TypeScript type annotations.',
  },

  {
    id: 'observability-comprehensive',
    check: (s) =>
      (s.saas_billing_module === 'enabled' || s.saas_app_module === 'enabled') &&
      !s.saas_observability_sentry &&
      !s.saas_observability_datadog &&
      !s.saas_observability_otel,
    message: 'Enable observability for production SaaS applications',
    severity: 'warning',
    affectedFields: [
      'saas_observability_sentry',
      'saas_observability_datadog',
      'saas_observability_otel',
    ],
    quickFix: {
      label: 'Enable Sentry',
      apply: () => ({ saas_observability_sentry: true }),
    },
    details:
      'Error tracking and performance monitoring are critical for production apps.',
  },

  {
    id: 'testing-comprehensive',
    check: (s) =>
      (s.saas_billing_module === 'enabled' || s.saas_app_module === 'enabled') &&
      s.saas_test_suite_level === 'standard',
    message: 'Comprehensive test suite recommended for production SaaS',
    severity: 'info',
    affectedFields: ['saas_test_suite_level'],
    quickFix: {
      label: 'Use comprehensive tests',
      apply: () => ({ saas_test_suite_level: 'comprehensive' }),
    },
    details:
      'Comprehensive suite includes integration tests, E2E tests, and load testing.',
  },

  {
    id: 'drizzle-cloudflare-recommend',
    check: (s) =>
      s.saas_hosting === 'cloudflare' && s.saas_orm === 'prisma',
    message: 'Drizzle ORM recommended for Cloudflare Workers',
    severity: 'info',
    affectedFields: ['saas_orm'],
    quickFix: {
      label: 'Use Drizzle ORM',
      apply: () => ({ saas_orm: 'drizzle' }),
    },
    details:
      'Drizzle has better edge runtime compatibility and smaller bundle size.',
  },

  {
    id: 'prisma-vercel-recommend',
    check: (s) =>
      s.saas_hosting === 'vercel' && s.saas_orm === 'drizzle',
    message: 'Prisma ORM recommended for Vercel deployments',
    severity: 'info',
    affectedFields: ['saas_orm'],
    quickFix: {
      label: 'Use Prisma ORM',
      apply: () => ({ saas_orm: 'prisma' }),
    },
    details: 'Prisma has excellent Vercel integration with serverless optimization.',
  },

  {
    id: 'email-saas-recommend',
    check: (s) =>
      (s.saas_auth_module === 'enabled' || s.saas_billing_module === 'enabled') &&
      s.saas_app_module !== 'enabled',
    message: 'Enable app layer for email notifications (verification, invoices)',
    severity: 'info',
    affectedFields: ['saas_app_module'],
    quickFix: {
      label: 'Enable app layer',
      apply: () => ({
        saas_app_module: 'enabled',
        saas_email: 'resend',
        saas_jobs: 'triggerdev',
      }),
    },
    details:
      'Transactional emails are essential for auth workflows and billing notifications.',
  },
]

/**
 * Validate configuration against all rules
 */
export function validateConfig(state: Partial<RisoConfig>): ValidationResult[] {
  return VALIDATION_RULES.filter((rule) => rule.check(state)).map(
    ({ id, message, severity, affectedFields, quickFix, details }) => ({
      id,
      message,
      severity,
      affectedFields,
      quickFix,
      details,
    })
  )
}

/**
 * Cost estimate for third-party services
 */
export interface CostEstimate {
  monthly: number
  services: Array<{ name: string; cost: number; note?: string }>
}

/**
 * Calculate estimated monthly costs for selected services
 */
export function getCostEstimate(state: Partial<RisoConfig>): CostEstimate {
  const services: CostEstimate['services'] = []

  // Authentication
  if (state.saas_auth_provider === 'clerk') {
    services.push({
      name: 'Clerk',
      cost: 0,
      note: 'Free up to 10k MAU',
    })
  } else if (state.saas_auth_provider === 'authjs') {
    services.push({
      name: 'Auth.js',
      cost: 0,
      note: 'Self-hosted, free',
    })
  } else if (state.saas_auth_provider === 'lucia') {
    services.push({
      name: 'Lucia',
      cost: 0,
      note: 'Self-hosted, free',
    })
  }

  // Enterprise bridge
  if (state.saas_enterprise_bridge === 'workos') {
    services.push({
      name: 'WorkOS',
      cost: 0,
      note: 'Free up to 1M MAU',
    })
  }

  // Billing
  if (state.saas_billing_provider === 'stripe') {
    services.push({
      name: 'Stripe',
      cost: 0,
      note: '2.9% + $0.30 per txn',
    })
  } else if (state.saas_billing_provider === 'paddle') {
    services.push({
      name: 'Paddle',
      cost: 0,
      note: '5% + $0.50 per txn',
    })
  } else if (state.saas_billing_provider === 'lemonsqueezy') {
    services.push({
      name: 'Lemon Squeezy',
      cost: 0,
      note: '5% per txn',
    })
  }

  // Database
  if (state.saas_database === 'neon') {
    services.push({
      name: 'Neon',
      cost: 0,
      note: 'Free tier: 3GB storage',
    })
  } else if (state.saas_database === 'supabase') {
    services.push({
      name: 'Supabase',
      cost: 0,
      note: 'Free tier: 500MB DB + 1GB storage',
    })
  }

  // Hosting
  if (state.saas_hosting === 'vercel') {
    services.push({
      name: 'Vercel',
      cost: 0,
      note: 'Free tier: 100GB bandwidth',
    })
  } else if (state.saas_hosting === 'cloudflare') {
    services.push({
      name: 'Cloudflare Pages',
      cost: 0,
      note: 'Free tier: 500 builds/month',
    })
  }

  // Email
  if (state.saas_email === 'resend') {
    services.push({
      name: 'Resend',
      cost: 0,
      note: 'Free tier: 3k emails/month',
    })
  } else if (state.saas_email === 'postmark') {
    services.push({
      name: 'Postmark',
      cost: 10,
      note: '10k emails/month',
    })
  }

  // Analytics
  if (state.saas_analytics === 'posthog') {
    services.push({
      name: 'PostHog',
      cost: 0,
      note: 'Free tier: 1M events/month',
    })
  } else if (state.saas_analytics === 'amplitude') {
    services.push({
      name: 'Amplitude',
      cost: 0,
      note: 'Free tier: 10M events/month',
    })
  }

  // Background jobs
  if (state.saas_jobs === 'triggerdev') {
    services.push({
      name: 'Trigger.dev',
      cost: 0,
      note: 'Free tier: 1M steps/month',
    })
  } else if (state.saas_jobs === 'inngest') {
    services.push({
      name: 'Inngest',
      cost: 0,
      note: 'Free tier: 100k steps/month',
    })
  }

  // Storage
  if (state.saas_storage === 'r2') {
    services.push({
      name: 'Cloudflare R2',
      cost: 0,
      note: 'Free tier: 10GB storage',
    })
  } else if (state.saas_storage === 'supabase-storage') {
    services.push({
      name: 'Supabase Storage',
      cost: 0,
      note: 'Included in Supabase plan',
    })
  }

  // AI
  if (state.saas_ai === 'openai') {
    services.push({
      name: 'OpenAI',
      cost: 0,
      note: 'Pay per token ($0.002-0.03/1k)',
    })
  } else if (state.saas_ai === 'anthropic') {
    services.push({
      name: 'Anthropic',
      cost: 0,
      note: 'Pay per token ($0.003-0.015/1k)',
    })
  }

  // Observability
  if (state.saas_observability_sentry) {
    services.push({
      name: 'Sentry',
      cost: 0,
      note: 'Free tier: 5k errors/month',
    })
  }
  if (state.saas_observability_datadog) {
    services.push({
      name: 'Datadog',
      cost: 0,
      note: 'Free tier: 1 host',
    })
  }

  // Search providers
  if (
    state.fumadocs_search_provider === 'algolia' ||
    state.docusaurus_search_provider === 'algolia'
  ) {
    services.push({
      name: 'Algolia',
      cost: 0,
      note: 'Free tier: 10k requests/month',
    })
  } else if (state.fumadocs_search_provider === 'orama-cloud') {
    services.push({
      name: 'Orama Cloud',
      cost: 0,
      note: 'Free tier: 100k ops/month',
    })
  }

  // Calculate total (only services with explicit monthly costs)
  const monthly = services.reduce((sum, s) => sum + s.cost, 0)

  return {
    monthly,
    services,
  }
}
