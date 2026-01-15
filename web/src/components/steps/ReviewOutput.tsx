import { useState } from 'react'
import { useRisoStore, type RisoConfig } from '../../lib/store'
import { Copy, Check, Download, Terminal, FileCode } from 'lucide-react'
import { stringify } from 'yaml'
import { cn, copyToClipboard, downloadFile } from '../../lib/utils'

type OutputMode = 'cli' | 'yaml'

export function ReviewOutput() {
  const { config, resetConfig, saveToHistory } = useRisoStore()
  const [mode, setMode] = useState<OutputMode>('cli')
  const [copied, setCopied] = useState(false)
  const [saveName, setSaveName] = useState('')

  const cliCommand = generateCliCommand(config)
  const yamlConfig = generateYamlConfig(config)

  const handleCopy = async () => {
    const text = mode === 'cli' ? cliCommand : yamlConfig
    await copyToClipboard(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    if (mode === 'yaml') {
      downloadFile(yamlConfig, 'copier-answers.yml', 'text/yaml')
    } else {
      downloadFile(cliCommand, 'riso-command.sh', 'text/x-shellscript')
    }
  }

  const handleSave = () => {
    if (saveName.trim()) {
      saveToHistory(saveName.trim())
      setSaveName('')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-display font-semibold text-gray-900 dark:text-white">Review & Generate</h2>
        <p className="mt-1 text-gray-500 dark:text-gray-400">
          Copy the command or download a ready-to-use answers file.
        </p>
      </div>

      {/* Output Mode Toggle */}
      <div className="flex gap-2 p-1 bg-white/80 dark:bg-gray-900/70 rounded-xl border border-white/70 dark:border-gray-800/70 w-fit">
        <button
          onClick={() => setMode('cli')}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
            mode === 'cli'
              ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
              : 'text-gray-600 dark:text-gray-300 hover:text-gray-900'
          )}
        >
          <Terminal className="h-4 w-4" />
          CLI Command
        </button>
        <button
          onClick={() => setMode('yaml')}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
            mode === 'yaml'
              ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
              : 'text-gray-600 dark:text-gray-300 hover:text-gray-900'
          )}
        >
          <FileCode className="h-4 w-4" />
          YAML Config
        </button>
      </div>

      {/* Output Display */}
      <div className="relative">
        <pre className="bg-gray-900 text-gray-100 p-4 rounded-xl overflow-x-auto text-sm leading-relaxed max-h-96">
          <code>{mode === 'cli' ? cliCommand : yamlConfig}</code>
        </pre>

        <div className="absolute top-2 right-2 flex gap-2">
          <button
            onClick={handleCopy}
            className="p-2 bg-gray-800 hover:bg-gray-700 rounded-md text-gray-300 hover:text-white transition-colors"
            title="Copy to clipboard"
          >
            {copied ? <Check className="h-4 w-4 text-green-400" /> : <Copy className="h-4 w-4" />}
          </button>
          <span className="sr-only" aria-live="polite">
            {copied ? 'Copied to clipboard' : ''}
          </span>
          <button
            onClick={handleDownload}
            className="p-2 bg-gray-800 hover:bg-gray-700 rounded-md text-gray-300 hover:text-white transition-colors"
            title="Download file"
          >
            <Download className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Usage Instructions */}
      <div className="p-4 bg-blue-50/80 dark:bg-blue-900/20 border border-blue-200/80 dark:border-blue-800/60 rounded-xl">
        {mode === 'cli' ? (
          <div className="space-y-2">
            <p className="text-sm font-medium text-blue-800 dark:text-blue-200">Usage:</p>
            <p className="text-sm text-blue-700 dark:text-blue-300">
              1. Copy the command above<br />
              2. Open your terminal<br />
              3. Navigate to your projects directory<br />
              4. Paste and run the command
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-sm font-medium text-blue-800 dark:text-blue-200">Usage:</p>
            <p className="text-sm text-blue-700 dark:text-blue-300">
              1. Download the <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">copier-answers.yml</code> file<br />
              2. Place it in your project directory<br />
              3. Run: <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">copier copy gh:wyattowalsh/riso . --answers-file copier-answers.yml</code>
            </p>
          </div>
        )}
      </div>

      {/* Save Configuration */}
      <div className="flex gap-3 items-center p-4 riso-card-soft rounded-xl">
        <input
          type="text"
          value={saveName}
          onChange={(e) => setSaveName(e.target.value)}
          placeholder="Configuration name..."
          className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:border-riso-500 focus:ring-riso-500"
        />
        <button
          onClick={handleSave}
          disabled={!saveName.trim()}
          className="px-4 py-2 bg-riso-500 text-white rounded-lg text-sm font-medium hover:bg-riso-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Save to History
        </button>
        <button
          onClick={resetConfig}
          className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          Reset
        </button>
      </div>

      {/* Configuration Summary */}
      <ConfigSummary config={config} />
    </div>
  )
}

function ConfigSummary({ config }: { config: Partial<RisoConfig> }) {
  const enabledModules = [
    config.cli_module === 'enabled' && 'CLI',
    config.api_tracks !== 'none' && `API (${config.api_tracks})`,
    config.graphql_api_module === 'enabled' && 'GraphQL',
    config.websocket_module === 'enabled' && 'WebSocket',
    config.mcp_module === 'enabled' && 'MCP',
    config.changelog_module === 'enabled' && 'Changelog',
    config.saas_starter_module === 'enabled' && 'SaaS Starter',
    config.ai_tools_module === 'enabled' && 'AI Tools',
  ].filter(Boolean)

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <SummaryCard title="Project" items={[
        `Name: ${config.project_name || 'Not set'}`,
        `Layout: ${config.project_layout}`,
        `Quality: ${config.quality_profile}`,
      ]} />
      <SummaryCard title="Modules" items={enabledModules.length > 0 ? enabledModules as string[] : ['None enabled']} />
      <SummaryCard title="Documentation" items={[
        config.docs_site !== 'none' ? config.docs_site || 'fumadocs' : 'Disabled',
      ]} />
    </div>
  )
}

function SummaryCard({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="p-4 riso-card-soft rounded-xl">
      <h4 className="font-medium text-gray-900 dark:text-white mb-2">{title}</h4>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li key={i} className="text-sm text-gray-600 dark:text-gray-400">{item}</li>
        ))}
      </ul>
    </div>
  )
}

function generateCliCommand(config: Partial<RisoConfig>): string {
  const projectName = config.project_name || 'my-project'
  const args: string[] = []

  // Core settings
  if (config.project_name) args.push(`project_name="${config.project_name}"`)
  if (config.project_layout) args.push(`project_layout="${config.project_layout}"`)
  if (config.quality_profile) args.push(`quality_profile="${config.quality_profile}"`)
  if (config.ci_platform) args.push(`ci_platform="${config.ci_platform}"`)

  // Modules
  if (config.cli_module) args.push(`cli_module="${config.cli_module}"`)
  if (config.api_tracks) args.push(`api_tracks="${config.api_tracks}"`)
  if (config.graphql_api_module) args.push(`graphql_api_module="${config.graphql_api_module}"`)
  if (config.websocket_module) args.push(`websocket_module="${config.websocket_module}"`)
  if (config.mcp_module) args.push(`mcp_module="${config.mcp_module}"`)
  if (config.codegen_module) args.push(`codegen_module="${config.codegen_module}"`)
  if (config.changelog_module) args.push(`changelog_module="${config.changelog_module}"`)
  if (config.shared_logic) args.push(`shared_logic="${config.shared_logic}"`)

  // Documentation
  if (config.docs_site) args.push(`docs_site="${config.docs_site}"`)

  // Fumadocs options
  if (config.docs_site === 'fumadocs') {
    if (config.fumadocs_search_provider) args.push(`fumadocs_search_provider="${config.fumadocs_search_provider}"`)
    if (config.fumadocs_theme) args.push(`fumadocs_theme="${config.fumadocs_theme}"`)
    if (config.fumadocs_llms_txt) args.push(`fumadocs_llms_txt="${config.fumadocs_llms_txt}"`)
    if (config.fumadocs_openapi) args.push(`fumadocs_openapi="${config.fumadocs_openapi}"`)
    if (config.fumadocs_blog) args.push(`fumadocs_blog="${config.fumadocs_blog}"`)
    if (config.fumadocs_mermaid) args.push(`fumadocs_mermaid="${config.fumadocs_mermaid}"`)
    if (config.fumadocs_math) args.push(`fumadocs_math="${config.fumadocs_math}"`)
  }

  // Docusaurus options
  if (config.docs_site === 'docusaurus') {
    if (config.docusaurus_search_provider) args.push(`docusaurus_search_provider="${config.docusaurus_search_provider}"`)
    if (config.docusaurus_theme) args.push(`docusaurus_theme="${config.docusaurus_theme}"`)
    if (config.docusaurus_analytics) args.push(`docusaurus_analytics="${config.docusaurus_analytics}"`)
    if (config.docusaurus_blog) args.push(`docusaurus_blog="${config.docusaurus_blog}"`)
    if (config.docusaurus_faster) args.push(`docusaurus_faster="${config.docusaurus_faster}"`)
  }

  // SaaS Starter
  if (config.saas_starter_module) args.push(`saas_starter_module="${config.saas_starter_module}"`)
  if (config.saas_starter_module === 'enabled') {
    if (config.saas_runtime) args.push(`saas_runtime="${config.saas_runtime}"`)
    if (config.saas_hosting) args.push(`saas_hosting="${config.saas_hosting}"`)
    if (config.saas_database) args.push(`saas_database="${config.saas_database}"`)
    if (config.saas_orm) args.push(`saas_orm="${config.saas_orm}"`)
    if (config.saas_auth) args.push(`saas_auth="${config.saas_auth}"`)
    if (config.saas_billing) args.push(`saas_billing="${config.saas_billing}"`)
    if (config.saas_jobs) args.push(`saas_jobs="${config.saas_jobs}"`)
    if (config.saas_email) args.push(`saas_email="${config.saas_email}"`)
    if (config.saas_analytics) args.push(`saas_analytics="${config.saas_analytics}"`)
    if (config.saas_ai) args.push(`saas_ai="${config.saas_ai}"`)
    if (config.saas_storage) args.push(`saas_storage="${config.saas_storage}"`)
    if (config.saas_enterprise_bridge) args.push(`saas_enterprise_bridge="${config.saas_enterprise_bridge}"`)
  }

  // AI Tools
  if (config.ai_tools_module) args.push(`ai_tools_module="${config.ai_tools_module}"`)
  if (config.ai_tools_module === 'enabled') {
    if (config.ai_tools_mcp_thinking !== undefined) args.push(`ai_tools_mcp_thinking=${config.ai_tools_mcp_thinking}`)
    if (config.ai_tools_mcp_web !== undefined) args.push(`ai_tools_mcp_web=${config.ai_tools_mcp_web}`)
    if (config.ai_tools_mcp_documents !== undefined) args.push(`ai_tools_mcp_documents=${config.ai_tools_mcp_documents}`)
    if (config.ai_tools_mcp_utilities !== undefined) args.push(`ai_tools_mcp_utilities=${config.ai_tools_mcp_utilities}`)
    if (config.ai_tools_mcp_search !== undefined) args.push(`ai_tools_mcp_search=${config.ai_tools_mcp_search}`)
  }

  const dataArgs = args.map(arg => `  --data ${arg}`).join(' \\\n')

  return `copier copy gh:wyattowalsh/riso ./${projectName} \\
${dataArgs}`
}

function generateYamlConfig(config: Partial<RisoConfig>): string {
  const yamlObj: Record<string, unknown> = {}

  // Core settings
  if (config.project_name) yamlObj.project_name = config.project_name
  if (config.project_layout) yamlObj.project_layout = config.project_layout
  if (config.quality_profile) yamlObj.quality_profile = config.quality_profile
  if (config.ci_platform) yamlObj.ci_platform = config.ci_platform

  // Modules
  if (config.cli_module) yamlObj.cli_module = config.cli_module
  if (config.api_tracks) yamlObj.api_tracks = config.api_tracks
  if (config.graphql_api_module) yamlObj.graphql_api_module = config.graphql_api_module
  if (config.websocket_module) yamlObj.websocket_module = config.websocket_module
  if (config.mcp_module) yamlObj.mcp_module = config.mcp_module
  if (config.codegen_module) yamlObj.codegen_module = config.codegen_module
  if (config.changelog_module) yamlObj.changelog_module = config.changelog_module
  if (config.shared_logic) yamlObj.shared_logic = config.shared_logic

  // Documentation
  if (config.docs_site) yamlObj.docs_site = config.docs_site

  // Fumadocs options
  if (config.docs_site === 'fumadocs') {
    if (config.fumadocs_search_provider) yamlObj.fumadocs_search_provider = config.fumadocs_search_provider
    if (config.fumadocs_theme) yamlObj.fumadocs_theme = config.fumadocs_theme
    if (config.fumadocs_code_theme) yamlObj.fumadocs_code_theme = config.fumadocs_code_theme
    if (config.fumadocs_toc_depth) yamlObj.fumadocs_toc_depth = config.fumadocs_toc_depth
    if (config.fumadocs_llms_txt) yamlObj.fumadocs_llms_txt = config.fumadocs_llms_txt
    if (config.fumadocs_openapi) yamlObj.fumadocs_openapi = config.fumadocs_openapi
    if (config.fumadocs_blog) yamlObj.fumadocs_blog = config.fumadocs_blog
    if (config.fumadocs_mermaid) yamlObj.fumadocs_mermaid = config.fumadocs_mermaid
    if (config.fumadocs_math) yamlObj.fumadocs_math = config.fumadocs_math
    if (config.fumadocs_image_zoom) yamlObj.fumadocs_image_zoom = config.fumadocs_image_zoom
    if (config.fumadocs_last_updated) yamlObj.fumadocs_last_updated = config.fumadocs_last_updated
    if (config.fumadocs_edit_on_github) yamlObj.fumadocs_edit_on_github = config.fumadocs_edit_on_github
    if (config.fumadocs_i18n) yamlObj.fumadocs_i18n = config.fumadocs_i18n
  }

  // Docusaurus options
  if (config.docs_site === 'docusaurus') {
    if (config.docusaurus_search_provider) yamlObj.docusaurus_search_provider = config.docusaurus_search_provider
    if (config.docusaurus_theme) yamlObj.docusaurus_theme = config.docusaurus_theme
    if (config.docusaurus_analytics) yamlObj.docusaurus_analytics = config.docusaurus_analytics
    if (config.docusaurus_comments) yamlObj.docusaurus_comments = config.docusaurus_comments
    if (config.docusaurus_llms_txt) yamlObj.docusaurus_llms_txt = config.docusaurus_llms_txt
    if (config.docusaurus_faster) yamlObj.docusaurus_faster = config.docusaurus_faster
    if (config.docusaurus_blog) yamlObj.docusaurus_blog = config.docusaurus_blog
    if (config.docusaurus_mermaid) yamlObj.docusaurus_mermaid = config.docusaurus_mermaid
    if (config.docusaurus_math) yamlObj.docusaurus_math = config.docusaurus_math
    if (config.docusaurus_versioning) yamlObj.docusaurus_versioning = config.docusaurus_versioning
    if (config.docusaurus_pwa) yamlObj.docusaurus_pwa = config.docusaurus_pwa
    if (config.docusaurus_i18n) yamlObj.docusaurus_i18n = config.docusaurus_i18n
    if (config.docusaurus_sitemap) yamlObj.docusaurus_sitemap = config.docusaurus_sitemap
  }

  // SaaS Starter
  if (config.saas_starter_module) yamlObj.saas_starter_module = config.saas_starter_module
  if (config.saas_starter_module === 'enabled') {
    if (config.saas_runtime) yamlObj.saas_runtime = config.saas_runtime
    if (config.saas_hosting) yamlObj.saas_hosting = config.saas_hosting
    if (config.saas_database) yamlObj.saas_database = config.saas_database
    if (config.saas_orm) yamlObj.saas_orm = config.saas_orm
    if (config.saas_auth) yamlObj.saas_auth = config.saas_auth
    if (config.saas_billing) yamlObj.saas_billing = config.saas_billing
    if (config.saas_jobs) yamlObj.saas_jobs = config.saas_jobs
    if (config.saas_email) yamlObj.saas_email = config.saas_email
    if (config.saas_analytics) yamlObj.saas_analytics = config.saas_analytics
    if (config.saas_ai) yamlObj.saas_ai = config.saas_ai
    if (config.saas_storage) yamlObj.saas_storage = config.saas_storage
    if (config.saas_enterprise_bridge) yamlObj.saas_enterprise_bridge = config.saas_enterprise_bridge
    if (config.saas_observability_sentry !== undefined) yamlObj.saas_observability_sentry = config.saas_observability_sentry
    if (config.saas_observability_datadog !== undefined) yamlObj.saas_observability_datadog = config.saas_observability_datadog
    if (config.saas_observability_otel !== undefined) yamlObj.saas_observability_otel = config.saas_observability_otel
    if (config.saas_observability_structured_logging !== undefined) yamlObj.saas_observability_structured_logging = config.saas_observability_structured_logging
  }

  // AI Tools
  if (config.ai_tools_module) yamlObj.ai_tools_module = config.ai_tools_module
  if (config.ai_tools_module === 'enabled') {
    if (config.ai_tools_mcp_thinking !== undefined) yamlObj.ai_tools_mcp_thinking = config.ai_tools_mcp_thinking
    if (config.ai_tools_mcp_web !== undefined) yamlObj.ai_tools_mcp_web = config.ai_tools_mcp_web
    if (config.ai_tools_mcp_documents !== undefined) yamlObj.ai_tools_mcp_documents = config.ai_tools_mcp_documents
    if (config.ai_tools_mcp_utilities !== undefined) yamlObj.ai_tools_mcp_utilities = config.ai_tools_mcp_utilities
    if (config.ai_tools_mcp_search !== undefined) yamlObj.ai_tools_mcp_search = config.ai_tools_mcp_search
  }

  const header = `# Riso Configuration
# Generated: ${new Date().toISOString()}
# Usage: copier copy gh:wyattowalsh/riso . --answers-file copier-answers.yml

`
  return header + stringify(yamlObj)
}
