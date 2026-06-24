import { useRisoStore, type RisoConfig } from '../../lib/store'
import { buildChoiceOptions } from '../../lib/matrixData'
import { cn } from '../../lib/utils'
import { Layers, Shield, CreditCard, Rocket, ChevronRight, Check } from 'lucide-react'

interface LayerCardProps {
  title: string
  description: string
  icon: React.ElementType
  enabled: boolean
  onToggle: (enabled: boolean) => void
  children?: React.ReactNode
  accentColor: string
  iconColor: string
  disabled?: boolean
  disabledReason?: string
  isComplete?: boolean
}

function LayerCard({
  title,
  description,
  icon: Icon,
  enabled,
  onToggle,
  children,
  accentColor,
  iconColor,
  disabled = false,
  disabledReason,
  isComplete = false,
}: LayerCardProps) {
  return (
    <div
      className={cn(
        'rounded-xl border-2 transition-all',
        disabled
          ? 'border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/30 opacity-60'
          : enabled
            ? accentColor
            : 'border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/30'
      )}
    >
      <div className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div
              className={cn(
                'p-2 rounded-lg transition-colors',
                enabled && !disabled ? accentColor : 'bg-gray-100 dark:bg-gray-700'
              )}
            >
              <Icon
                className={cn('h-5 w-5', enabled && !disabled ? iconColor : 'text-gray-400')}
              />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-gray-900 dark:text-white">{title}</h3>
                {isComplete && enabled && (
                  <span className="flex items-center gap-1 text-xs text-riso-green dark:text-riso-mint font-medium">
                    <Check className="h-3 w-3" />
                    Ready
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{description}</p>
              {disabled && disabledReason && (
                <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">{disabledReason}</p>
              )}
            </div>
          </div>
          <button
            type="button"
            disabled={disabled}
            onClick={() => onToggle(!enabled)}
            className={cn(
              'relative inline-flex h-6 w-11 flex-shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out',
              disabled
                ? 'cursor-not-allowed bg-gray-200 dark:bg-gray-600'
                : enabled
                  ? 'cursor-pointer bg-riso-orange'
                  : 'cursor-pointer bg-gray-200 dark:bg-gray-600'
            )}
          >
            <span
              className={cn(
                'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                enabled ? 'translate-x-5' : 'translate-x-0'
              )}
            />
          </button>
        </div>
      </div>

      {enabled && !disabled && children && (
        <div className="px-4 pb-4">
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">{children}</div>
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
      <div className="grid gap-2 sm:grid-cols-2">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            aria-pressed={value === option.value}
            className={cn(
              'p-3 rounded-lg border text-left transition-all',
              value === option.value
                ? 'border-riso-orange bg-riso-orange/10 dark:bg-riso-orange/5'
                : 'border-gray-200 dark:border-gray-700 hover:border-riso-orange/50'
            )}
          >
            <div className="font-medium text-sm text-gray-900 dark:text-white">{option.label}</div>
            {option.description && (
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {option.description}
              </div>
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
    <label className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 dark:border-gray-700 cursor-pointer hover:border-riso-orange/50 transition-colors">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 rounded border-gray-300 text-riso-orange focus:ring-riso-orange accent-riso-orange"
      />
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</span>
    </label>
  )
}

export function SaaSConfig() {
  const { config, updateConfig } = useRisoStore()

  // Layer states with defaults
  const infraEnabled = config.saas_infra_module === 'enabled'
  const authEnabled = config.saas_auth_module === 'enabled'
  const billingEnabled = config.saas_billing_module === 'enabled'
  const appEnabled = config.saas_app_module === 'enabled'

  // Build options from matrix data
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

  const authProviderOptions = buildChoiceOptions({
    key: 'saas_auth_provider',
    fallbackChoices: ['clerk', 'authjs', 'lucia'],
    labels: {
      clerk: 'Clerk',
      authjs: 'Auth.js',
      lucia: 'Lucia',
    },
    descriptions: {
      clerk: 'Hosted, built-in UI, passkeys',
      authjs: 'Self-hosted, full control',
      lucia: 'Lightweight, session-based',
    },
  })

  const billingProviderOptions = buildChoiceOptions({
    key: 'saas_billing_provider',
    fallbackChoices: ['stripe', 'paddle', 'lemonsqueezy'],
    labels: {
      stripe: 'Stripe',
      paddle: 'Paddle',
      lemonsqueezy: 'LemonSqueezy',
    },
    descriptions: {
      stripe: 'Full control, widest ecosystem',
      paddle: 'Merchant of Record, auto tax',
      lemonsqueezy: 'Simple MoR, indie-friendly',
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

  // Handle layer toggle with cascading disables
  const handleInfraToggle = (enabled: boolean) => {
    updateConfig({ saas_infra_module: enabled ? 'enabled' : 'disabled' })
    if (!enabled) {
      // Disable dependent layers
      updateConfig({
        saas_auth_module: 'disabled',
        saas_billing_module: 'disabled',
        saas_app_module: 'disabled',
      })
    }
  }

  const handleAuthToggle = (enabled: boolean) => {
    updateConfig({ saas_auth_module: enabled ? 'enabled' : 'disabled' })
    if (!enabled) {
      // Disable dependent layers
      updateConfig({
        saas_billing_module: 'disabled',
        saas_app_module: 'disabled',
      })
    }
  }

  const handleBillingToggle = (enabled: boolean) => {
    updateConfig({ saas_billing_module: enabled ? 'enabled' : 'disabled' })
    if (!enabled) {
      // Disable dependent layer
      updateConfig({ saas_app_module: 'disabled' })
    }
  }

  const handleAppToggle = (enabled: boolean) => {
    updateConfig({ saas_app_module: enabled ? 'enabled' : 'disabled' })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="display-md text-gray-900 dark:text-white">SaaS Stack</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Build your SaaS in layers. Each layer unlocks the next.
        </p>
      </div>

      {/* Layer Progress Indicator */}
      <div className="flex items-center gap-2 p-3 rounded-lg bg-gray-100 dark:bg-gray-800/50">
        <div className="flex items-center gap-1">
          {[
            { enabled: infraEnabled, label: 'Infra' },
            { enabled: authEnabled, label: 'Auth' },
            { enabled: billingEnabled, label: 'Billing' },
            { enabled: appEnabled, label: 'App' },
          ].map((layer, i, arr) => (
            <div key={layer.label} className="flex items-center">
              <div
                className={cn(
                  'px-2 py-1 rounded text-xs font-medium transition-colors',
                  layer.enabled
                    ? 'bg-riso-orange text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                )}
              >
                {layer.label}
              </div>
              {i < arr.length - 1 && (
                <ChevronRight className="h-4 w-4 text-gray-400 mx-1" />
              )}
            </div>
          ))}
        </div>
        <span className="ml-auto text-xs text-gray-500 dark:text-gray-400">
          {[infraEnabled, authEnabled, billingEnabled, appEnabled].filter(Boolean).length}/4 layers
        </span>
      </div>

      <div className="space-y-4">
        {/* Layer 1: Infrastructure */}
        <LayerCard
          title="Layer 1: Infrastructure"
          description="Runtime, hosting, database, and ORM foundation"
          icon={Layers}
          enabled={infraEnabled}
          onToggle={handleInfraToggle}
          accentColor="border-riso-orange/30 bg-riso-orange/5"
          iconColor="text-riso-orange"
          isComplete={infraEnabled}
        >
          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <CategorySelect
                label="Runtime Framework"
                value={config.saas_runtime || 'nextjs-16'}
                onChange={(v) => updateConfig({ saas_runtime: v as RisoConfig['saas_runtime'] })}
                options={runtimeOptions}
              />
              <CategorySelect
                label="Hosting Platform"
                value={config.saas_hosting || 'vercel'}
                onChange={(v) => updateConfig({ saas_hosting: v as RisoConfig['saas_hosting'] })}
                options={hostingOptions}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <CategorySelect
                label="Database"
                value={config.saas_database || 'neon'}
                onChange={(v) => updateConfig({ saas_database: v as RisoConfig['saas_database'] })}
                options={databaseOptions}
              />
              <CategorySelect
                label="ORM"
                value={config.saas_orm || 'prisma'}
                onChange={(v) => updateConfig({ saas_orm: v as RisoConfig['saas_orm'] })}
                options={ormOptions}
              />
            </div>
          </div>
        </LayerCard>

        {/* Layer 2: Authentication */}
        <LayerCard
          title="Layer 2: Authentication"
          description="User auth, sessions, and identity management"
          icon={Shield}
          enabled={authEnabled}
          onToggle={handleAuthToggle}
          accentColor="border-riso-teal/30 bg-riso-teal/5"
          iconColor="text-riso-teal dark:text-riso-mint"
          disabled={!infraEnabled}
          disabledReason="Enable Infrastructure layer first"
          isComplete={authEnabled}
        >
          <CategorySelect
            label="Auth Provider"
            value={config.saas_auth_provider || 'clerk'}
            onChange={(v) =>
              updateConfig({ saas_auth_provider: v as RisoConfig['saas_auth_provider'] })
            }
            options={authProviderOptions}
          />
        </LayerCard>

        {/* Layer 3: Billing */}
        <LayerCard
          title="Layer 3: Billing"
          description="Subscriptions, payments, and monetization"
          icon={CreditCard}
          enabled={billingEnabled}
          onToggle={handleBillingToggle}
          accentColor="border-riso-grape/30 bg-riso-grape/5"
          iconColor="text-riso-grape dark:text-riso-fluorescent-pink"
          disabled={!authEnabled}
          disabledReason="Enable Authentication layer first"
          isComplete={billingEnabled}
        >
          <CategorySelect
            label="Billing Provider"
            value={config.saas_billing_provider || 'stripe'}
            onChange={(v) =>
              updateConfig({ saas_billing_provider: v as RisoConfig['saas_billing_provider'] })
            }
            options={billingProviderOptions}
          />
        </LayerCard>

        {/* Layer 4: Application */}
        <LayerCard
          title="Layer 4: Application"
          description="Analytics, AI, email, jobs, and features"
          icon={Rocket}
          enabled={appEnabled}
          onToggle={handleAppToggle}
          accentColor="border-riso-green/30 bg-riso-green/5"
          iconColor="text-riso-green dark:text-riso-mint"
          disabled={!billingEnabled}
          disabledReason="Enable Billing layer first"
          isComplete={appEnabled}
        >
          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <CategorySelect
                label="Analytics"
                value={config.saas_analytics || 'posthog'}
                onChange={(v) => updateConfig({ saas_analytics: v as RisoConfig['saas_analytics'] })}
                options={analyticsOptions}
              />
              <CategorySelect
                label="AI Provider"
                value={config.saas_ai || 'openai'}
                onChange={(v) => updateConfig({ saas_ai: v as RisoConfig['saas_ai'] })}
                options={aiOptions}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <CategorySelect
                label="Email"
                value={config.saas_email || 'resend'}
                onChange={(v) => updateConfig({ saas_email: v as RisoConfig['saas_email'] })}
                options={emailOptions}
              />
              <CategorySelect
                label="Background Jobs"
                value={config.saas_jobs || 'triggerdev'}
                onChange={(v) => updateConfig({ saas_jobs: v as RisoConfig['saas_jobs'] })}
                options={jobsOptions}
              />
            </div>

            {/* Observability toggles */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Observability
              </label>
              <div className="grid gap-2 sm:grid-cols-2">
                <ToggleCheckbox
                  label="Sentry (Error Tracking)"
                  checked={config.saas_observability_sentry ?? true}
                  onChange={(v) => updateConfig({ saas_observability_sentry: v })}
                />
                <ToggleCheckbox
                  label="Datadog (APM)"
                  checked={config.saas_observability_datadog ?? true}
                  onChange={(v) => updateConfig({ saas_observability_datadog: v })}
                />
                <ToggleCheckbox
                  label="OpenTelemetry"
                  checked={config.saas_observability_otel ?? true}
                  onChange={(v) => updateConfig({ saas_observability_otel: v })}
                />
                <ToggleCheckbox
                  label="Structured Logging"
                  checked={config.saas_observability_structured_logging ?? true}
                  onChange={(v) => updateConfig({ saas_observability_structured_logging: v })}
                />
              </div>
            </div>
          </div>
        </LayerCard>
      </div>

      {/* Quick tip */}
      {!infraEnabled && (
        <div className="p-4 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
          <p className="text-sm text-amber-800 dark:text-amber-200">
            <strong>Tip:</strong> Enable Infrastructure to unlock the full SaaS stack. Each layer
            builds on the previous one.
          </p>
        </div>
      )}
    </div>
  )
}
