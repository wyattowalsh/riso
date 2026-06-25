import { useState } from 'react'
import { useRisoStore, type RisoConfig } from '../../lib/store'
import { Copy, Check, Download, Terminal, FileCode, Settings2, FolderTree } from 'lucide-react'
import { stringify } from 'yaml'
import { cn, copyToClipboard, downloadFile } from '../../lib/utils'
import { DependencyWarnings, DependencyBadge } from '../DependencyWarnings'
import { FileTreePreview } from '../FileTreePreview'

type OutputMode = 'cli' | 'yaml'
type TabType = 'configuration' | 'file-preview' | 'cli-command'

interface TabConfig {
  id: TabType
  label: string
  icon: React.ComponentType<{ className?: string }>
}

const TABS: TabConfig[] = [
  { id: 'configuration', label: 'Configuration', icon: Settings2 },
  { id: 'file-preview', label: 'File Preview', icon: FolderTree },
  { id: 'cli-command', label: 'CLI Command', icon: Terminal },
]

export function ReviewOutput() {
  const { config, resetConfig, saveToHistory } = useRisoStore()
  const [activeTab, setActiveTab] = useState<TabType>('configuration')
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
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-display font-semibold text-gray-900 dark:text-white">Review & Generate</h2>
          <p className="mt-1 text-gray-500 dark:text-gray-400">
            Copy the command or download a ready-to-use answers file.
          </p>
        </div>
        <DependencyBadge />
      </div>

      {/* Dependency Warnings */}
      <DependencyWarnings showEmpty />

      {/* Tabbed Interface */}
      <div className="riso-card rounded-xl overflow-hidden">
        {/* Tab Bar */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
          {TABS.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'relative flex items-center gap-2 px-5 py-3.5 text-sm font-medium transition-all duration-200',
                  'hover:bg-white/50 dark:hover:bg-gray-700/50',
                  isActive
                    ? 'text-riso-federal-blue dark:text-riso-cornflower bg-white dark:bg-gray-800'
                    : 'text-gray-500 dark:text-gray-400'
                )}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
                {/* Active tab indicator */}
                {isActive && (
                  <span
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-riso-federal-blue dark:bg-riso-cornflower transition-transform duration-300"
                  />
                )}
              </button>
            )
          })}
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Configuration Tab */}
          <div
            className={cn(
              'transition-all duration-300',
              activeTab === 'configuration'
                ? 'opacity-100 translate-y-0'
                : 'hidden opacity-0 translate-y-2'
            )}
          >
            <ConfigurationTabContent config={config} />
          </div>

          {/* File Preview Tab */}
          <div
            className={cn(
              'transition-all duration-300',
              activeTab === 'file-preview'
                ? 'opacity-100 translate-y-0'
                : 'hidden opacity-0 translate-y-2'
            )}
          >
            <FilePreviewTabContent config={config} />
          </div>

          {/* CLI Command Tab */}
          <div
            className={cn(
              'transition-all duration-300',
              activeTab === 'cli-command'
                ? 'opacity-100 translate-y-0'
                : 'hidden opacity-0 translate-y-2'
            )}
          >
            <CLICommandTabContent
              mode={mode}
              setMode={setMode}
              cliCommand={cliCommand}
              yamlConfig={yamlConfig}
              copied={copied}
              handleCopy={handleCopy}
              handleDownload={handleDownload}
            />
          </div>
        </div>
      </div>

      {/* Save Configuration */}
      <div className="flex gap-3 items-center p-4 riso-card-soft rounded-xl">
        <input
          type="text"
          value={saveName}
          onChange={(e) => setSaveName(e.target.value)}
          placeholder="Configuration name..."
          className="input-riso flex-1"
        />
        <button
          onClick={handleSave}
          disabled={!saveName.trim()}
          className="btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Save to History
        </button>
        <button
          onClick={resetConfig}
          className="btn-ghost text-sm"
        >
          Reset
        </button>
      </div>
    </div>
  )
}

// Configuration Tab Content Component
function ConfigurationTabContent({ config }: { config: Partial<RisoConfig> }) {
  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2">
        <ConfigSummary config={config} />
        <QuickStats config={config} />
      </div>
    </div>
  )
}

// File Preview Tab Content Component
function FilePreviewTabContent({ config }: { config: Partial<RisoConfig> }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Project File Structure
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Preview the files and folders that will be generated based on your configuration.
          </p>
        </div>
      </div>
      <FileTreePreview config={config} className="border-0 shadow-none p-0" />
    </div>
  )
}

// CLI Command Tab Content Component
function CLICommandTabContent({
  mode,
  setMode,
  cliCommand,
  yamlConfig,
  copied,
  handleCopy,
  handleDownload,
}: {
  mode: OutputMode
  setMode: (mode: OutputMode) => void
  cliCommand: string
  yamlConfig: string
  copied: boolean
  handleCopy: () => void
  handleDownload: () => void
}) {
  return (
    <div className="space-y-5">
      {/* Output Mode Toggle */}
      <div className="flex gap-1 p-1 rounded-xl bg-gray-100 dark:bg-gray-800 w-fit">
        <button
          onClick={() => setMode('cli')}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
            mode === 'cli'
              ? 'bg-white dark:bg-gray-700 shadow-sm text-riso-federal-blue'
              : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
          )}
        >
          <Terminal className="h-4 w-4" />
          CLI Command
        </button>
        <button
          onClick={() => setMode('yaml')}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
            mode === 'yaml'
              ? 'bg-white dark:bg-gray-700 shadow-sm text-riso-federal-blue'
              : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
          )}
        >
          <FileCode className="h-4 w-4" />
          YAML Config
        </button>
      </div>

      {/* Output Display */}
      <div className="relative">
        <pre className="bg-riso-ink-black text-gray-100 rounded-xl p-5 overflow-x-auto text-sm font-mono max-h-96">
          <code>{mode === 'cli' ? cliCommand : yamlConfig}</code>
        </pre>

        <div className="absolute top-3 right-3 flex gap-2">
          <button
            onClick={handleCopy}
            className="btn-secondary text-sm px-3 py-1.5 transition-all"
            title="Copy to clipboard"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4 inline-block mr-1" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="h-4 w-4 inline-block mr-1" />
                Copy
              </>
            )}
          </button>
          <span className="sr-only" aria-live="polite">
            {copied ? 'Copied to clipboard' : ''}
          </span>
          <button
            onClick={handleDownload}
            className="btn-secondary text-sm px-3 py-1.5"
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
    </div>
  )
}

// Quick Stats Component for Configuration Tab
function QuickStats({ config }: { config: Partial<RisoConfig> }) {
  const enabledModulesCount = [
    config.cli_module === 'enabled',
    config.api_module === 'enabled',
    config.mcp_module === 'enabled',
    config.docs_module === 'enabled',
    config.codegen_module === 'enabled',
    config.changelog_module === 'enabled',
    config.ai_tools_module === 'enabled',
  ].filter(Boolean).length

  const saasLayersCount = [
    config.saas_infra_module === 'enabled',
    config.saas_auth_module === 'enabled',
    config.saas_billing_module === 'enabled',
    config.saas_app_module === 'enabled',
  ].filter(Boolean).length

  const languagesUsed = new Set<string>()
  if (config.cli_module === 'enabled' && config.cli_languages) {
    config.cli_languages.forEach(lang => languagesUsed.add(lang))
  }
  if (config.api_module === 'enabled' && config.api_languages) {
    config.api_languages.forEach(lang => languagesUsed.add(lang))
  }
  if (config.mcp_module === 'enabled' && config.mcp_languages) {
    config.mcp_languages.forEach(lang => languagesUsed.add(lang))
  }

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-medium text-gray-900 dark:text-white">
        Quick Stats
      </h4>
      <div className="grid grid-cols-2 gap-3">
        <StatCard label="Modules" value={enabledModulesCount} color="blue" />
        <StatCard label="SaaS Layers" value={saasLayersCount} color="orange" />
        <StatCard label="Languages" value={languagesUsed.size || 1} color="green" />
        <StatCard
          label="Layout"
          value={config.project_layout === 'monorepo' ? 'Mono' : 'Single'}
          color="purple"
          isText
        />
      </div>
    </div>
  )
}

function StatCard({
  label,
  value,
  color,
  isText = false,
}: {
  label: string
  value: number | string
  color: 'blue' | 'orange' | 'green' | 'purple'
  isText?: boolean
}) {
  const colorClasses = {
    blue: 'from-riso-federal-blue to-riso-cornflower',
    orange: 'from-riso-orange to-riso-apricot',
    green: 'from-riso-green to-riso-mint',
    purple: 'from-riso-grape to-riso-fluorescent-pink',
  }

  return (
    <div className="p-4 riso-card-soft rounded-xl">
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
        {label}
      </p>
      <p
        className={cn(
          'font-display font-bold bg-gradient-to-r bg-clip-text text-transparent',
          colorClasses[color],
          isText ? 'text-lg' : 'text-2xl'
        )}
      >
        {value}
      </p>
    </div>
  )
}

function ConfigSummary({ config }: { config: Partial<RisoConfig> }) {
  const formatLangs = (langs: string[] | undefined): string => {
    if (!langs || langs.length === 0) return 'python'
    return langs.join(', ')
  }

  const enabledModules = [
    config.cli_module === 'enabled' && `CLI (${formatLangs(config.cli_languages)})`,
    config.api_module === 'enabled' && `API (${formatLangs(config.api_languages)})`,
    config.mcp_module === 'enabled' && `MCP (${formatLangs(config.mcp_languages)})`,
    config.codegen_module === 'enabled' && 'Codegen',
    config.changelog_module === 'enabled' && 'Changelog',
    config.ai_tools_module === 'enabled' && 'AI Tools',
  ].filter(Boolean)

  const saasLayers = [
    config.saas_infra_module === 'enabled' && 'Infrastructure',
    config.saas_auth_module === 'enabled' && 'Auth',
    config.saas_billing_module === 'enabled' && 'Billing',
    config.saas_app_module === 'enabled' && 'App',
  ].filter(Boolean)

  const docsInfo = config.docs_module === 'enabled'
    ? config.docs_framework || 'fumadocs'
    : 'Disabled'

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-medium text-gray-900 dark:text-white">
        Configuration Summary
      </h4>
      <div className="grid gap-3">
        <SummaryCard title="Project" items={[
          `Name: ${config.project_name || 'Not set'}`,
          `Layout: ${config.project_layout}`,
          `Quality: ${config.quality_profile}`,
          `Task runner: ${config.task_runner || 'just'}`,
        ]} />
        <SummaryCard title="Modules" items={enabledModules.length > 0 ? enabledModules as string[] : ['None enabled']} />
        <SummaryCard title="Documentation" items={[docsInfo]} />
        <SummaryCard title="SaaS Layers" items={saasLayers.length > 0 ? saasLayers as string[] : ['Not enabled']} />
      </div>
    </div>
  )
}

function SummaryCard({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="p-3 riso-card-soft rounded-xl">
      <h4 className="font-medium text-gray-900 dark:text-white mb-1.5 text-sm">{title}</h4>
      <ul className="space-y-0.5">
        {items.map((item, i) => (
          <li key={i} className="text-xs text-gray-600 dark:text-gray-400">{item}</li>
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

  // CLI Module
  if (config.cli_module) args.push(`cli_module="${config.cli_module}"`)
  if (config.cli_module === 'enabled' && config.cli_languages?.length) {
    args.push(`cli_languages='${JSON.stringify(config.cli_languages)}'`)
  }

  // API Module
  if (config.api_module) args.push(`api_module="${config.api_module}"`)
  if (config.api_module === 'enabled') {
    if (config.api_languages?.length) args.push(`api_languages='${JSON.stringify(config.api_languages)}'`)
    if (config.api_features && config.api_features !== 'none') args.push(`api_features="${config.api_features}"`)
  }

  // MCP Module
  if (config.mcp_module) args.push(`mcp_module="${config.mcp_module}"`)
  if (config.mcp_module === 'enabled' && config.mcp_languages?.length) {
    args.push(`mcp_languages='${JSON.stringify(config.mcp_languages)}'`)
  }

  // Documentation
  if (config.docs_module) args.push(`docs_module="${config.docs_module}"`)
  if (config.docs_module === 'enabled' && config.docs_framework) {
    args.push(`docs_framework="${config.docs_framework}"`)
  }

  // Other modules
  if (config.codegen_module) args.push(`codegen_module="${config.codegen_module}"`)
  if (config.changelog_module) args.push(`changelog_module="${config.changelog_module}"`)
  if (config.shared_logic) args.push(`shared_logic="${config.shared_logic}"`)

  // Fumadocs options
  if (config.docs_module === 'enabled' && config.docs_framework === 'fumadocs') {
    if (config.fumadocs_search_provider) args.push(`fumadocs_search_provider="${config.fumadocs_search_provider}"`)
    if (config.fumadocs_theme) args.push(`fumadocs_theme="${config.fumadocs_theme}"`)
    if (config.fumadocs_llms_txt) args.push(`fumadocs_llms_txt="${config.fumadocs_llms_txt}"`)
    if (config.fumadocs_openapi) args.push(`fumadocs_openapi="${config.fumadocs_openapi}"`)
    if (config.fumadocs_blog) args.push(`fumadocs_blog="${config.fumadocs_blog}"`)
    if (config.fumadocs_mermaid) args.push(`fumadocs_mermaid="${config.fumadocs_mermaid}"`)
    if (config.fumadocs_math) args.push(`fumadocs_math="${config.fumadocs_math}"`)
  }

  // Docusaurus options
  if (config.docs_module === 'enabled' && config.docs_framework === 'docusaurus') {
    if (config.docusaurus_search_provider) args.push(`docusaurus_search_provider="${config.docusaurus_search_provider}"`)
    if (config.docusaurus_theme) args.push(`docusaurus_theme="${config.docusaurus_theme}"`)
    if (config.docusaurus_analytics) args.push(`docusaurus_analytics="${config.docusaurus_analytics}"`)
    if (config.docusaurus_blog) args.push(`docusaurus_blog="${config.docusaurus_blog}"`)
    if (config.docusaurus_faster) args.push(`docusaurus_faster="${config.docusaurus_faster}"`)
  }

  // SaaS Layers
  if (config.saas_infra_module) args.push(`saas_infra_module="${config.saas_infra_module}"`)
  if (config.saas_infra_module === 'enabled') {
    if (config.saas_runtime) args.push(`saas_runtime="${config.saas_runtime}"`)
    if (config.saas_hosting) args.push(`saas_hosting="${config.saas_hosting}"`)
    if (config.saas_database) args.push(`saas_database="${config.saas_database}"`)
    if (config.saas_orm) args.push(`saas_orm="${config.saas_orm}"`)
  }
  if (config.saas_auth_module) args.push(`saas_auth_module="${config.saas_auth_module}"`)
  if (config.saas_auth_module === 'enabled') {
    if (config.saas_auth_provider) args.push(`saas_auth_provider="${config.saas_auth_provider}"`)
    if (config.saas_enterprise_bridge) args.push(`saas_enterprise_bridge="${config.saas_enterprise_bridge}"`)
  }
  if (config.saas_billing_module) args.push(`saas_billing_module="${config.saas_billing_module}"`)
  if (config.saas_billing_module === 'enabled') {
    if (config.saas_billing_provider) args.push(`saas_billing_provider="${config.saas_billing_provider}"`)
  }
  if (config.saas_app_module) args.push(`saas_app_module="${config.saas_app_module}"`)
  if (config.saas_app_module === 'enabled') {
    if (config.saas_jobs) args.push(`saas_jobs="${config.saas_jobs}"`)
    if (config.saas_email) args.push(`saas_email="${config.saas_email}"`)
    if (config.saas_analytics) args.push(`saas_analytics="${config.saas_analytics}"`)
    if (config.saas_ai) args.push(`saas_ai="${config.saas_ai}"`)
    if (config.saas_storage) args.push(`saas_storage="${config.saas_storage}"`)
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

  // CLI Module
  if (config.cli_module) yamlObj.cli_module = config.cli_module
  if (config.cli_module === 'enabled' && config.cli_languages?.length) {
    yamlObj.cli_languages = config.cli_languages
  }

  // API Module
  if (config.api_module) yamlObj.api_module = config.api_module
  if (config.api_module === 'enabled') {
    if (config.api_languages?.length) yamlObj.api_languages = config.api_languages
    if (config.api_features && config.api_features !== 'none') yamlObj.api_features = config.api_features
  }

  // MCP Module
  if (config.mcp_module) yamlObj.mcp_module = config.mcp_module
  if (config.mcp_module === 'enabled' && config.mcp_languages?.length) {
    yamlObj.mcp_languages = config.mcp_languages
  }

  // Documentation
  if (config.docs_module) yamlObj.docs_module = config.docs_module
  if (config.docs_module === 'enabled' && config.docs_framework) {
    yamlObj.docs_framework = config.docs_framework
  }

  // Other modules
  if (config.codegen_module) yamlObj.codegen_module = config.codegen_module
  if (config.changelog_module) yamlObj.changelog_module = config.changelog_module
  if (config.shared_logic) yamlObj.shared_logic = config.shared_logic

  // Fumadocs options
  if (config.docs_module === 'enabled' && config.docs_framework === 'fumadocs') {
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
  if (config.docs_module === 'enabled' && config.docs_framework === 'docusaurus') {
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

  // SaaS Layers
  if (config.saas_infra_module) yamlObj.saas_infra_module = config.saas_infra_module
  if (config.saas_infra_module === 'enabled') {
    if (config.saas_runtime) yamlObj.saas_runtime = config.saas_runtime
    if (config.saas_hosting) yamlObj.saas_hosting = config.saas_hosting
    if (config.saas_database) yamlObj.saas_database = config.saas_database
    if (config.saas_orm) yamlObj.saas_orm = config.saas_orm
  }
  if (config.saas_auth_module) yamlObj.saas_auth_module = config.saas_auth_module
  if (config.saas_auth_module === 'enabled') {
    if (config.saas_auth_provider) yamlObj.saas_auth_provider = config.saas_auth_provider
    if (config.saas_enterprise_bridge) yamlObj.saas_enterprise_bridge = config.saas_enterprise_bridge
  }
  if (config.saas_billing_module) yamlObj.saas_billing_module = config.saas_billing_module
  if (config.saas_billing_module === 'enabled') {
    if (config.saas_billing_provider) yamlObj.saas_billing_provider = config.saas_billing_provider
  }
  if (config.saas_app_module) yamlObj.saas_app_module = config.saas_app_module
  if (config.saas_app_module === 'enabled') {
    if (config.saas_jobs) yamlObj.saas_jobs = config.saas_jobs
    if (config.saas_email) yamlObj.saas_email = config.saas_email
    if (config.saas_analytics) yamlObj.saas_analytics = config.saas_analytics
    if (config.saas_ai) yamlObj.saas_ai = config.saas_ai
    if (config.saas_storage) yamlObj.saas_storage = config.saas_storage
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
