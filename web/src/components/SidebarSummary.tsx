import { BookOpen, CheckCircle2, Sparkles } from 'lucide-react'
import { useRisoStore } from '../lib/store'
import { WIZARD_STEPS } from '../lib/wizardSteps'

export function SidebarSummary() {
  const { config, currentStep, setStep } = useRisoStore()

  const enabledModules = [
    config.cli_module === 'enabled' && 'CLI',
    config.api_tracks !== 'none' && `API (${config.api_tracks})`,
    config.graphql_api_module === 'enabled' && 'GraphQL',
    config.websocket_module === 'enabled' && 'WebSocket',
    config.mcp_module === 'enabled' && 'MCP',
    config.changelog_module === 'enabled' && 'Changelog',
    config.saas_starter_module === 'enabled' && 'SaaS Starter',
    config.ai_tools_module === 'enabled' && 'AI Tools',
  ].filter(Boolean) as string[]

  const stepLabel = WIZARD_STEPS[currentStep]?.name ?? 'Project'
  const progress = ((currentStep + 1) / WIZARD_STEPS.length) * 100

  return (
    <aside className="space-y-6 lg:sticky lg:top-24">
      <div className="riso-card p-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">Progress</p>
            <p className="mt-1 text-sm font-semibold text-gray-900 dark:text-white">
              Step {currentStep + 1} of {WIZARD_STEPS.length}: {stepLabel}
            </p>
          </div>
          <CheckCircle2 className="h-5 w-5 text-riso-500" />
        </div>
        <div className="mt-3 h-2 rounded-full bg-gray-100 dark:bg-gray-800 overflow-hidden">
          <div
            className="h-full rounded-full bg-riso-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="riso-card-soft p-5">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Configuration Snapshot</h3>
        <dl className="mt-3 space-y-2 text-sm text-gray-600 dark:text-gray-300">
          <div className="flex items-center justify-between gap-3">
            <dt className="text-gray-500">Project</dt>
            <dd className="font-medium text-gray-900 dark:text-white">
              {config.project_name || 'Untitled'}
            </dd>
          </div>
          <div className="flex items-center justify-between gap-3">
            <dt className="text-gray-500">Layout</dt>
            <dd>{config.project_layout ?? 'single-package'}</dd>
          </div>
          <div className="flex items-center justify-between gap-3">
            <dt className="text-gray-500">Quality</dt>
            <dd>{config.quality_profile ?? 'standard'}</dd>
          </div>
          <div className="flex items-center justify-between gap-3">
            <dt className="text-gray-500">Docs</dt>
            <dd>{config.docs_site !== 'none' ? config.docs_site ?? 'fumadocs' : 'Disabled'}</dd>
          </div>
        </dl>
        {!config.project_name && (
          <p className="mt-3 text-xs text-amber-600 dark:text-amber-400">
            Tip: add a project name to personalize your Copier command.
          </p>
        )}
      </div>

      <div className="riso-card-soft p-5">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Enabled Modules</h3>
        {enabledModules.length > 0 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {enabledModules.map((module) => (
              <span
                key={module}
                className="rounded-full border border-gray-200/80 dark:border-gray-700/60 bg-white/80 dark:bg-gray-900/70 px-3 py-1 text-xs font-semibold text-gray-600 dark:text-gray-300"
              >
                {module}
              </span>
            ))}
          </div>
        ) : (
          <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">No modules enabled yet.</p>
        )}
      </div>

      <div className="riso-card p-5">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Quick Actions</h3>
        <div className="mt-4 flex flex-col gap-3">
          <button
            onClick={() => setStep(WIZARD_STEPS.length - 1)}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-riso-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-riso-500/20 transition hover:bg-riso-600"
          >
            <Sparkles className="h-4 w-4" />
            Jump to Review
          </button>
          <a
            href="/docs/"
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-200/80 dark:border-gray-700/70 bg-white/80 dark:bg-gray-900/70 px-4 py-2 text-sm font-semibold text-gray-700 dark:text-gray-200 transition hover:border-riso-300 hover:text-riso-600 dark:hover:text-riso-400"
          >
            <BookOpen className="h-4 w-4" />
            Read the Docs
          </a>
        </div>
      </div>
    </aside>
  )
}
