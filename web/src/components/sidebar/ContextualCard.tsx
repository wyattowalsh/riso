import { useRisoStore } from '../../lib/store'
import { cn } from '../../lib/utils'
import {
  Sparkles, Layers, BookOpen, Rocket, Cpu, CheckCircle2,
  Terminal, Server, FileCode
} from 'lucide-react'

const MODULE_QUICK_TOGGLES = [
  { key: 'cli_module', label: 'CLI', icon: Terminal },
  { key: 'api_module', label: 'API', icon: Server },
  { key: 'mcp_module', label: 'MCP', icon: FileCode },
  { key: 'docs_module', label: 'Docs', icon: BookOpen },
]

const DOCS_FRAMEWORKS = [
  { id: 'fumadocs', name: 'Fumadocs', desc: 'Next.js, fast, modern' },
  { id: 'docusaurus', name: 'Docusaurus', desc: 'React, feature-rich' },
  { id: 'sphinx-shibuya', name: 'Sphinx', desc: 'Python native, mature' },
]

interface ContextualCardProps {
  currentStep: number
}

export function ContextualCard({ currentStep }: ContextualCardProps) {
  const { config, updateConfig } = useRisoStore()

  // Step 0: Project - Minimal progress
  if (currentStep === 0) {
    return (
      <div className="text-center py-6">
        <Sparkles className="h-8 w-8 mx-auto text-riso-sunflower mb-3" />
        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Let's set up your project
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Name, layout, and quality profile
        </p>
      </div>
    )
  }

  // Step 1: Modules - Quick toggles
  if (currentStep === 1) {
    return (
      <div className="space-y-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center gap-2">
          <Layers className="h-3.5 w-3.5 text-riso-teal" />
          Quick Add
        </h4>
        <div className="grid grid-cols-2 gap-2">
          {MODULE_QUICK_TOGGLES.map(({ key, label, icon: Icon }) => {
            const isEnabled = config[key as keyof typeof config] === 'enabled'
            return (
              <button
                key={key}
                onClick={() => updateConfig({ [key]: isEnabled ? 'disabled' : 'enabled' })}
                className={cn(
                  'flex items-center gap-2 p-2.5 rounded-lg text-xs font-medium transition-all',
                  isEnabled
                    ? 'bg-riso-teal/10 text-riso-teal border border-riso-teal/30'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 border border-transparent hover:border-gray-300 dark:hover:border-gray-600'
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
                {isEnabled && <CheckCircle2 className="h-3 w-3 ml-auto" />}
              </button>
            )
          })}
        </div>
      </div>
    )
  }

  // Step 2: Docs - Framework comparison
  if (currentStep === 2) {
    return (
      <div className="space-y-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center gap-2">
          <BookOpen className="h-3.5 w-3.5 text-riso-sunflower" />
          Frameworks
        </h4>
        <div className="space-y-2">
          {DOCS_FRAMEWORKS.map((fw) => {
            const isSelected = config.docs_framework === fw.id
            return (
              <button
                key={fw.id}
                onClick={() => updateConfig({ docs_framework: fw.id as 'fumadocs' | 'sphinx-shibuya' | 'docusaurus', docs_module: 'enabled' })}
                className={cn(
                  'w-full text-left p-2.5 rounded-lg text-xs transition-all',
                  isSelected
                    ? 'bg-riso-sunflower/10 border border-riso-sunflower/30'
                    : 'bg-gray-50 dark:bg-gray-800/50 border border-transparent hover:border-gray-200 dark:hover:border-gray-700'
                )}
              >
                <div className="font-medium text-gray-900 dark:text-white">{fw.name}</div>
                <div className="text-gray-500 dark:text-gray-400">{fw.desc}</div>
              </button>
            )
          })}
        </div>
      </div>
    )
  }

  // Step 3: SaaS - Cost estimate (only show enabled layers)
  if (currentStep === 3) {
    const hasInfra = config.saas_infra_module === 'enabled'
    const hasAuth = config.saas_auth_module === 'enabled'
    const hasBilling = config.saas_billing_module === 'enabled'
    const hasApp = config.saas_app_module === 'enabled'

    // Calculate estimated monthly cost based on enabled layers
    let estimatedMonthly = 0
    if (hasAuth) estimatedMonthly += 25 // Clerk base cost
    if (hasApp && config.saas_analytics === 'posthog') estimatedMonthly += 0 // PostHog free tier

    const hasAnyCost = hasInfra || hasAuth || hasBilling || hasApp

    return (
      <div className="space-y-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center gap-2">
          <Rocket className="h-3.5 w-3.5 text-riso-fluorescent-pink" />
          Cost Preview
        </h4>
        {hasAnyCost ? (
          <div className="space-y-2 text-xs">
            {hasInfra && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">
                    {config.saas_hosting === 'cloudflare' ? 'Cloudflare' : 'Vercel'}
                  </span>
                  <span className="text-gray-900 dark:text-white">Free tier</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">
                    {config.saas_database === 'supabase' ? 'Supabase' : 'Neon'} DB
                  </span>
                  <span className="text-gray-900 dark:text-white">Free tier</span>
                </div>
              </>
            )}
            {hasAuth && (
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">
                  {config.saas_enterprise_bridge === 'workos'
                    ? 'Clerk + WorkOS'
                    : config.saas_auth_provider === 'authjs'
                      ? 'Auth.js'
                      : config.saas_auth_provider === 'lucia'
                        ? 'Lucia'
                        : 'Clerk'} Auth
                </span>
                <span className="text-gray-900 dark:text-white">~$25/mo</span>
              </div>
            )}
            {hasBilling && (
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">
                  {config.saas_billing_provider === 'lemonsqueezy' ? 'LemonSqueezy' : 'Stripe'}
                </span>
                <span className="text-gray-900 dark:text-white">2.9% + 30c</span>
              </div>
            )}
            {hasApp && config.saas_analytics && (
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Analytics</span>
                <span className="text-gray-900 dark:text-white">Free tier</span>
              </div>
            )}
            <div className="pt-2 border-t border-gray-200 dark:border-gray-700 flex justify-between font-medium">
              <span className="text-gray-700 dark:text-gray-300">Est. Monthly</span>
              <span className="text-riso-green">
                {estimatedMonthly > 0 ? `~$${estimatedMonthly}+` : 'Free tier'}
              </span>
            </div>
          </div>
        ) : (
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Enable SaaS module to see cost estimates
          </p>
        )}
      </div>
    )
  }

  // Step 4: AI Tools - Checklist
  if (currentStep === 4) {
    return (
      <div className="space-y-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center gap-2">
          <Cpu className="h-3.5 w-3.5 text-riso-green" />
          AI Integration
        </h4>
        <div className="space-y-2 text-xs">
          {[
            { label: 'Claude Code files', done: true },
            { label: 'Cursor rules', done: true },
            { label: 'Copilot config', done: true },
            { label: 'OpenCode config', done: config.ai_tools_module === 'enabled' },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-2">
              <div className={cn(
                'h-4 w-4 rounded-full flex items-center justify-center',
                item.done ? 'bg-riso-green/10' : 'bg-gray-100 dark:bg-gray-800'
              )}>
                {item.done && <CheckCircle2 className="h-3 w-3 text-riso-green" />}
              </div>
              <span className={item.done ? 'text-gray-900 dark:text-white' : 'text-gray-400'}>
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Step 5: Review - Full summary (compact)
  if (currentStep === 5) {
    // Count modules consistently with ReviewOutput.tsx QuickStats
    const enabledCount = [
      config.cli_module, config.api_module, config.mcp_module,
      config.docs_module, config.codegen_module, config.changelog_module,
      config.ai_tools_module
    ].filter(v => v === 'enabled').length

    return (
      <div className="space-y-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center gap-2">
          <CheckCircle2 className="h-3.5 w-3.5 text-riso-grape" />
          Summary
        </h4>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-500 dark:text-gray-400">Project</span>
            <span className="text-gray-900 dark:text-white font-medium truncate max-w-[100px]">
              {config.project_name || 'Untitled'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500 dark:text-gray-400">Layout</span>
            <span className="text-gray-900 dark:text-white">{config.project_layout || 'single'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500 dark:text-gray-400">Modules</span>
            <span className="text-riso-federal-blue dark:text-riso-cornflower font-bold">{enabledCount}</span>
          </div>
        </div>
      </div>
    )
  }

  return null
}
