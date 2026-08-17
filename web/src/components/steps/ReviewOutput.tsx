import { useState, type KeyboardEvent } from 'react'
import { useRisoStore, type RisoConfig } from '../../lib/store'
import { generateCliCommand, generateYamlConfig } from '../../lib/exportConfig'
import { useValidation } from '../../lib/useValidation'
import { Copy, Check, Download, Terminal, FileCode, Settings2, FolderTree } from 'lucide-react'
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
  const { config, resetConfig, saveToHistory, updateConfig } = useRisoStore()
  const { errors } = useValidation(config, updateConfig)
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

      {errors.length > 0 && (
        <div
          role="alert"
          className="rounded-lg border border-red-300/80 bg-red-50 px-4 py-3 text-sm text-red-900 dark:border-red-700 dark:bg-red-950/40 dark:text-red-100"
        >
          <p className="font-medium">Configuration has {errors.length} blocking issue(s).</p>
          <p className="mt-1 text-red-800/90 dark:text-red-200/90">
            Review the issues listed above before running the generated command.
          </p>
        </div>
      )}

      {/* Tabbed Interface */}
      <div className="riso-card rounded-xl overflow-hidden">
        {/* Tab Bar */}
        <div
          role="tablist"
          aria-label="Review output sections"
          className="flex border-b border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50"
        >
          {TABS.map((tab, index) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            const panelId = `review-tab-panel-${tab.id}`
            const onTabKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
              if (!['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(event.key)) return
              event.preventDefault()
              let nextIndex = index
              if (event.key === 'ArrowRight') nextIndex = (index + 1) % TABS.length
              if (event.key === 'ArrowLeft') nextIndex = (index - 1 + TABS.length) % TABS.length
              if (event.key === 'Home') nextIndex = 0
              if (event.key === 'End') nextIndex = TABS.length - 1
              const nextTab = TABS[nextIndex]
              setActiveTab(nextTab.id)
              document.getElementById(`review-tab-${nextTab.id}`)?.focus()
            }
            return (
              <button
                key={tab.id}
                id={`review-tab-${tab.id}`}
                role="tab"
                type="button"
                aria-selected={isActive}
                aria-controls={panelId}
                tabIndex={isActive ? 0 : -1}
                onClick={() => setActiveTab(tab.id)}
                onKeyDown={onTabKeyDown}
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
            id="review-tab-panel-configuration"
            role="tabpanel"
            aria-labelledby="review-tab-configuration"
            hidden={activeTab !== 'configuration'}
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
            id="review-tab-panel-file-preview"
            role="tabpanel"
            aria-labelledby="review-tab-file-preview"
            hidden={activeTab !== 'file-preview'}
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
            id="review-tab-panel-cli-command"
            role="tabpanel"
            aria-labelledby="review-tab-cli-command"
            hidden={activeTab !== 'cli-command'}
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
        <label htmlFor="save-config-name" className="sr-only">
          Configuration name
        </label>
        <input
          id="save-config-name"
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
            type="button"
            onClick={handleDownload}
            className="btn-secondary text-sm px-3 py-1.5"
            title="Download file"
            aria-label={
              mode === 'yaml'
                ? 'Download YAML answers file'
                : 'Download CLI command script'
            }
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
              3. Run: <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">uv run riso copy --answers-file copier-answers.yml</code>
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
