import { useRisoStore, type RisoConfig } from '../../lib/store'
import { buildChoiceOptions, getPromptDefault, getPromptHelpSummary } from '../../lib/matrixData'
import { cn } from '../../lib/utils'

export function SaaSConfig() {
  const { config, updateConfig } = useRisoStore()
  const isEnabled =
    (config.saas_starter_module ??
      getPromptDefault<'enabled' | 'disabled'>('saas_starter_module', 'disabled')) ===
    'enabled'
  const moduleHelp = getPromptHelpSummary('saas_starter_module')

  const runtimeOptions = buildChoiceOptions({
    key: 'saas_runtime',
    fallbackChoices: ['nextjs-16', 'remix-2'],
    labels: {
      'nextjs-16': 'Next.js 16',
      'remix-2': 'Remix 2.x',
    },
    descriptions: {
      'nextjs-16': 'React 19, App Router, Turbopack',
      'remix-2': 'Server-first, explicit data loading',
    },
  })

  const hostingOptions = buildChoiceOptions({
    key: 'saas_hosting',
    fallbackChoices: ['vercel', 'cloudflare'],
    labels: {
      vercel: 'Vercel',
      cloudflare: 'Cloudflare',
    },
    descriptions: {
      vercel: 'Native Next.js, edge functions',
      cloudflare: 'Global edge, lower egress',
    },
  })

  const databaseOptions = buildChoiceOptions({
    key: 'saas_database',
    fallbackChoices: ['neon', 'supabase'],
    labels: {
      neon: 'Neon',
      supabase: 'Supabase',
    },
    descriptions: {
      neon: 'Serverless Postgres, branching',
      supabase: 'Postgres + Auth + Storage',
    },
  })

  const ormOptions = buildChoiceOptions({
    key: 'saas_orm',
    fallbackChoices: ['prisma', 'drizzle'],
    labels: {
      prisma: 'Prisma',
      drizzle: 'Drizzle',
    },
    descriptions: {
      prisma: 'Best TypeScript DX, migrations',
      drizzle: 'Lightweight, edge-optimized',
    },
  })

  const authOptions = buildChoiceOptions({
    key: 'saas_auth',
    fallbackChoices: ['clerk', 'authjs'],
    labels: {
      clerk: 'Clerk',
      authjs: 'Auth.js',
    },
    descriptions: {
      clerk: 'Hosted, built-in UI, passkeys',
      authjs: 'Self-hosted, full control',
    },
  })

  const billingOptions = buildChoiceOptions({
    key: 'saas_billing',
    fallbackChoices: ['stripe', 'paddle'],
    labels: {
      stripe: 'Stripe',
      paddle: 'Paddle',
    },
    descriptions: {
      stripe: 'Full control, widest ecosystem',
      paddle: 'Merchant of Record, auto tax',
    },
  })

  const jobsOptions = buildChoiceOptions({
    key: 'saas_jobs',
    fallbackChoices: ['triggerdev', 'inngest'],
    labels: {
      triggerdev: 'Trigger.dev',
      inngest: 'Inngest',
    },
    descriptions: {
      triggerdev: 'Task-centric, AI-optimized',
      inngest: 'Event-driven workflows',
    },
  })

  const emailOptions = buildChoiceOptions({
    key: 'saas_email',
    fallbackChoices: ['resend', 'postmark'],
    labels: {
      resend: 'Resend',
      postmark: 'Postmark',
    },
    descriptions: {
      resend: 'React Email, modern DX',
      postmark: 'Best deliverability',
    },
  })

  const analyticsOptions = buildChoiceOptions({
    key: 'saas_analytics',
    fallbackChoices: ['posthog', 'amplitude'],
    labels: {
      posthog: 'PostHog',
      amplitude: 'Amplitude',
    },
    descriptions: {
      posthog: 'Product OS, open-source',
      amplitude: 'Enterprise analytics',
    },
  })

  const aiOptions = buildChoiceOptions({
    key: 'saas_ai',
    fallbackChoices: ['openai', 'anthropic'],
    labels: {
      openai: 'OpenAI',
      anthropic: 'Anthropic',
    },
    descriptions: {
      openai: 'GPT-4o/5, largest ecosystem',
      anthropic: 'Claude 4.x, longer context',
    },
  })

  const storageOptions = buildChoiceOptions({
    key: 'saas_storage',
    fallbackChoices: ['r2', 'supabase-storage'],
    labels: {
      r2: 'Cloudflare R2',
      'supabase-storage': 'Supabase Storage',
    },
    descriptions: {
      r2: 'S3-compatible, zero egress',
      'supabase-storage': 'Integrated, RLS policies',
    },
  })

  const enterpriseOptions = buildChoiceOptions({
    key: 'saas_enterprise_bridge',
    fallbackChoices: ['none', 'workos'],
    labels: {
      none: 'None',
      workos: 'WorkOS',
    },
    descriptions: {
      none: 'Skip enterprise features',
      workos: 'SSO, SCIM, Directory Sync',
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-display font-semibold text-gray-900 dark:text-white">SaaS Starter</h2>
        <p className="mt-1 text-gray-500 dark:text-gray-400">
          Configure a production-grade SaaS stack across 14 categories.
        </p>
        {moduleHelp && <p className="mt-2 text-xs text-gray-500">{moduleHelp}</p>}
      </div>

      {/* Enable/Disable Toggle */}
      <div className="flex items-center gap-4 p-4 riso-card-soft rounded-xl">
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={isEnabled}
            onChange={(e) => updateConfig({ saas_starter_module: e.target.checked ? 'enabled' : 'disabled' })}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-riso-300/60 dark:peer-focus:ring-riso-800/60 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-riso-500"></div>
        </label>
        <span className="font-medium text-gray-900 dark:text-white">
          {isEnabled ? 'SaaS Starter Enabled' : 'SaaS Starter Disabled'}
        </span>
      </div>

      {isEnabled && (
        <div className="grid gap-6 sm:grid-cols-2">
          <CategorySelect
            label="Runtime Framework"
            value={
              config.saas_runtime ||
              getPromptDefault<RisoConfig['saas_runtime']>('saas_runtime', 'nextjs-16') ||
              'nextjs-16'
            }
            onChange={(v) => updateConfig({ saas_runtime: v as RisoConfig['saas_runtime'] })}
            options={runtimeOptions}
          />

          <CategorySelect
            label="Hosting Platform"
            value={
              config.saas_hosting ||
              getPromptDefault<RisoConfig['saas_hosting']>('saas_hosting', 'vercel') ||
              'vercel'
            }
            onChange={(v) => updateConfig({ saas_hosting: v as RisoConfig['saas_hosting'] })}
            options={hostingOptions}
          />

          <CategorySelect
            label="Database"
            value={
              config.saas_database ||
              getPromptDefault<RisoConfig['saas_database']>('saas_database', 'neon') ||
              'neon'
            }
            onChange={(v) => updateConfig({ saas_database: v as RisoConfig['saas_database'] })}
            options={databaseOptions}
          />

          <CategorySelect
            label="ORM"
            value={
              config.saas_orm ||
              getPromptDefault<RisoConfig['saas_orm']>('saas_orm', 'prisma') ||
              'prisma'
            }
            onChange={(v) => updateConfig({ saas_orm: v as RisoConfig['saas_orm'] })}
            options={ormOptions}
          />

          <CategorySelect
            label="Authentication"
            value={
              config.saas_auth ||
              getPromptDefault<RisoConfig['saas_auth']>('saas_auth', 'clerk') ||
              'clerk'
            }
            onChange={(v) => updateConfig({ saas_auth: v as RisoConfig['saas_auth'] })}
            options={authOptions}
          />

          <CategorySelect
            label="Billing"
            value={
              config.saas_billing ||
              getPromptDefault<RisoConfig['saas_billing']>('saas_billing', 'stripe') ||
              'stripe'
            }
            onChange={(v) => updateConfig({ saas_billing: v as RisoConfig['saas_billing'] })}
            options={billingOptions}
          />

          <CategorySelect
            label="Background Jobs"
            value={
              config.saas_jobs ||
              getPromptDefault<RisoConfig['saas_jobs']>('saas_jobs', 'triggerdev') ||
              'triggerdev'
            }
            onChange={(v) => updateConfig({ saas_jobs: v as RisoConfig['saas_jobs'] })}
            options={jobsOptions}
          />

          <CategorySelect
            label="Email"
            value={
              config.saas_email ||
              getPromptDefault<RisoConfig['saas_email']>('saas_email', 'resend') ||
              'resend'
            }
            onChange={(v) => updateConfig({ saas_email: v as RisoConfig['saas_email'] })}
            options={emailOptions}
          />

          <CategorySelect
            label="Analytics"
            value={
              config.saas_analytics ||
              getPromptDefault<RisoConfig['saas_analytics']>('saas_analytics', 'posthog') ||
              'posthog'
            }
            onChange={(v) => updateConfig({ saas_analytics: v as RisoConfig['saas_analytics'] })}
            options={analyticsOptions}
          />

          <CategorySelect
            label="AI Provider"
            value={
              config.saas_ai ||
              getPromptDefault<RisoConfig['saas_ai']>('saas_ai', 'openai') ||
              'openai'
            }
            onChange={(v) => updateConfig({ saas_ai: v as RisoConfig['saas_ai'] })}
            options={aiOptions}
          />

          <CategorySelect
            label="File Storage"
            value={
              config.saas_storage ||
              getPromptDefault<RisoConfig['saas_storage']>('saas_storage', 'r2') ||
              'r2'
            }
            onChange={(v) => updateConfig({ saas_storage: v as RisoConfig['saas_storage'] })}
            options={storageOptions}
          />

          <CategorySelect
            label="Enterprise SSO"
            value={
              config.saas_enterprise_bridge ||
              getPromptDefault<RisoConfig['saas_enterprise_bridge']>('saas_enterprise_bridge', 'none') ||
              'none'
            }
            onChange={(v) => updateConfig({ saas_enterprise_bridge: v as RisoConfig['saas_enterprise_bridge'] })}
            options={enterpriseOptions}
          />
        </div>
      )}

      {isEnabled && (
        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg space-y-3">
          <h3 className="font-medium text-gray-900 dark:text-white">Observability</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            <ToggleCheckbox
              label="Sentry (Error Tracking)"
              checked={
                config.saas_observability_sentry ??
                getPromptDefault<boolean>('saas_observability_sentry', true)
              }
              onChange={(v) => updateConfig({ saas_observability_sentry: v })}
            />
            <ToggleCheckbox
              label="Datadog (APM)"
              checked={
                config.saas_observability_datadog ??
                getPromptDefault<boolean>('saas_observability_datadog', true)
              }
              onChange={(v) => updateConfig({ saas_observability_datadog: v })}
            />
            <ToggleCheckbox
              label="OpenTelemetry"
              checked={
                config.saas_observability_otel ??
                getPromptDefault<boolean>('saas_observability_otel', true)
              }
              onChange={(v) => updateConfig({ saas_observability_otel: v })}
            />
            <ToggleCheckbox
              label="Structured Logging"
              checked={
                config.saas_observability_structured_logging ??
                getPromptDefault<boolean>('saas_observability_structured_logging', true)
              }
              onChange={(v) => updateConfig({ saas_observability_structured_logging: v })}
            />
          </div>
        </div>
      )}
    </div>
  )
}

function CategorySelect({
  label,
  value,
  onChange,
  options,
}: {
  label: string
  value: string
  onChange: (value: string) => void
  options: { value: string; label: string; description?: string }[]
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {label}
      </label>
      <div className="space-y-2">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            aria-pressed={value === option.value}
            className={cn(
              'w-full p-4 rounded-2xl border text-left transition-all hover:-translate-y-0.5 hover:shadow-md',
              value === option.value
                ? 'border-riso-500 bg-riso-50/80 dark:bg-riso-900/20'
                : 'border-white/70 dark:border-gray-700/60 bg-white/70 dark:bg-gray-900/60 hover:border-riso-300'
            )}
          >
            <div className="font-medium text-sm text-gray-900 dark:text-white">{option.label}</div>
            {option.description && (
              <div className="text-xs text-gray-500 dark:text-gray-400">{option.description}</div>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}

function ToggleCheckbox({
  label,
  checked,
  onChange,
}: {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  return (
    <label className="flex items-center gap-2 rounded-xl border border-white/70 dark:border-gray-700/60 bg-white/70 dark:bg-gray-900/60 px-3 py-2 cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 rounded border-gray-300 text-riso-500 focus:ring-riso-500"
      />
      <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
    </label>
  )
}
