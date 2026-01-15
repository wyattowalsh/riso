import { useRisoStore, type RisoConfig } from '../lib/store'
import { Sparkles, Zap, Server, Box, Rocket } from 'lucide-react'
import { cn } from '../lib/utils'
import { formatMatrixTimestamp, matrixMeta } from '../lib/matrixData'

interface Preset {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  config: Partial<RisoConfig>
}

const PRESETS: Preset[] = [
  {
    id: 'minimal-python',
    name: 'Minimal Python CLI',
    description: 'Lightweight Python package with CLI scaffolding',
    icon: <Box className="h-5 w-5" />,
    config: {
      project_layout: 'single-package',
      quality_profile: 'standard',
      cli_module: 'enabled',
      api_tracks: 'none',
      docs_site: 'none',
      saas_starter_module: 'disabled',
      ai_tools_module: 'enabled',
    },
  },
  {
    id: 'python-api',
    name: 'Python API Service',
    description: 'FastAPI with docs and quality tooling',
    icon: <Server className="h-5 w-5" />,
    config: {
      project_layout: 'single-package',
      quality_profile: 'standard',
      cli_module: 'disabled',
      api_tracks: 'python',
      graphql_api_module: 'disabled',
      websocket_module: 'disabled',
      docs_site: 'fumadocs',
      fumadocs_openapi: 'enabled',
      saas_starter_module: 'disabled',
      ai_tools_module: 'enabled',
    },
  },
  {
    id: 'fullstack',
    name: 'Full-Stack Python + Node',
    description: 'FastAPI backend + Fastify + Fumadocs',
    icon: <Zap className="h-5 w-5" />,
    config: {
      project_layout: 'monorepo',
      quality_profile: 'strict',
      cli_module: 'enabled',
      api_tracks: 'python+node',
      graphql_api_module: 'enabled',
      websocket_module: 'enabled',
      mcp_module: 'enabled',
      shared_logic: 'enabled',
      docs_site: 'fumadocs',
      fumadocs_openapi: 'enabled',
      fumadocs_llms_txt: 'enabled',
      saas_starter_module: 'disabled',
      ai_tools_module: 'enabled',
    },
  },
  {
    id: 'saas-starter',
    name: 'SaaS Starter',
    description: 'Production-ready SaaS with Next.js 16',
    icon: <Rocket className="h-5 w-5" />,
    config: {
      project_layout: 'monorepo',
      quality_profile: 'strict',
      api_tracks: 'node',
      docs_site: 'fumadocs',
      saas_starter_module: 'enabled',
      saas_runtime: 'nextjs-16',
      saas_hosting: 'vercel',
      saas_database: 'neon',
      saas_orm: 'prisma',
      saas_auth: 'clerk',
      saas_billing: 'stripe',
      saas_analytics: 'posthog',
      ai_tools_module: 'enabled',
    },
  },
  {
    id: 'docs-only',
    name: 'Documentation Site',
    description: 'Standalone Docusaurus docs site',
    icon: <Sparkles className="h-5 w-5" />,
    config: {
      project_layout: 'single-package',
      quality_profile: 'standard',
      cli_module: 'disabled',
      api_tracks: 'none',
      docs_site: 'docusaurus',
      docusaurus_faster: 'enabled',
      docusaurus_blog: 'enabled',
      docusaurus_mermaid: 'enabled',
      docusaurus_llms_txt: 'enabled',
      saas_starter_module: 'disabled',
      ai_tools_module: 'disabled',
    },
  },
]

export function Presets() {
  const { resetConfig, updateConfig, setStep } = useRisoStore()
  const matrixStamp = formatMatrixTimestamp(matrixMeta.generatedAt)

  const applyPreset = (preset: Preset) => {
    // Reset config first to clear any existing selections, then apply preset
    resetConfig()
    updateConfig(preset.config)
    setStep(5) // Jump to review step
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Quick Start Presets</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Jump to a curated configuration with one click.
        </p>
        <p className="text-xs text-gray-400 dark:text-gray-500">
          Options follow the matrix snapshot {matrixStamp ?? 'unknown'}.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {PRESETS.map((preset) => (
          <button
            key={preset.id}
            onClick={() => applyPreset(preset)}
            className={cn(
              'p-5 rounded-2xl border text-left transition-all hover:border-riso-300 hover:shadow-lg hover:-translate-y-0.5',
              'border-white/70 dark:border-gray-700/60 bg-white/80 dark:bg-gray-900/70'
            )}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-riso-100/80 dark:bg-riso-900/40 text-riso-600 dark:text-riso-300">
                {preset.icon}
              </div>
              <div className="font-medium text-gray-900 dark:text-white">{preset.name}</div>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">{preset.description}</p>
          </button>
        ))}
      </div>
    </div>
  )
}
