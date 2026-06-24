import { useRisoStore } from '../../lib/store'
import { Terminal, Server, Cpu, Code, Package, GitBranch } from 'lucide-react'
import {
  ModuleCard,
  LanguageSelector,
  FeatureToggleGroup,
  type LanguageOption,
  type ToggleOption
} from '../modules'

const CLI_LANGUAGES: LanguageOption[] = [
  { value: 'python', label: 'Python', description: 'Typer + Rich' },
  { value: 'rust', label: 'Rust', description: 'Clap + colored' },
  { value: 'go', label: 'Go', description: 'Cobra + Viper' },
  { value: 'typescript', label: 'TypeScript', description: 'Commander.js' },
]

const API_LANGUAGES: LanguageOption[] = [
  { value: 'python', label: 'Python', description: 'FastAPI' },
  { value: 'node', label: 'Node.js', description: 'Fastify' },
  { value: 'go', label: 'Go', description: 'Gin' },
  { value: 'rust', label: 'Rust', description: 'Actix-web' },
]

const MCP_LANGUAGES: LanguageOption[] = [
  { value: 'python', label: 'Python', description: 'fastmcp' },
  { value: 'typescript', label: 'TypeScript', description: 'MCP SDK' },
  { value: 'rust', label: 'Rust', description: 'mcp-rs' },
  { value: 'go', label: 'Go', description: 'mcp-go' },
]

const API_FEATURES: ToggleOption[] = [
  { value: 'none', label: 'REST Only', description: 'Standard REST API' },
  { value: 'graphql', label: '+ GraphQL', description: 'Add Strawberry GraphQL' },
  { value: 'websocket', label: '+ WebSocket', description: 'Add real-time support' },
  { value: 'graphql,websocket', label: '+ Both', description: 'GraphQL and WebSocket' },
]

const ENABLE_DISABLE: ToggleOption[] = [
  { value: 'disabled', label: 'Disabled' },
  { value: 'enabled', label: 'Enabled' },
]

export function ModulesConfig() {
  const { config, updateConfig } = useRisoStore()

  return (
    <div className="space-y-6">
      <div>
        <h2 className="display-md text-gray-900 dark:text-white">Components</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Each component can use a different language. Mix and match to build your ideal stack.
        </p>
      </div>

      <div className="space-y-4">
        {/* CLI Module */}
        <ModuleCard
          title="CLI Application"
          description="Command-line interface with argument parsing and rich output"
          icon={Terminal}
          enabled={config.cli_module === 'enabled'}
          onToggle={(enabled) => updateConfig({ cli_module: enabled ? 'enabled' : 'disabled' })}
          accentColor="blue"
        >
          <LanguageSelector
            label="Implementation Languages"
            helperText="(select multiple)"
            options={CLI_LANGUAGES}
            values={config.cli_languages || ['python']}
            onChange={(v) => updateConfig({ cli_languages: v as ('python' | 'rust' | 'go' | 'typescript')[] })}
          />
        </ModuleCard>

        {/* API Module */}
        <ModuleCard
          title="REST/HTTP API"
          description="Production-ready API server with automatic OpenAPI documentation"
          icon={Server}
          enabled={config.api_module === 'enabled'}
          onToggle={(enabled) => updateConfig({ api_module: enabled ? 'enabled' : 'disabled' })}
          accentColor="green"
        >
          <div className="space-y-4">
            <LanguageSelector
              label="Implementation Languages"
              helperText="(select multiple)"
              options={API_LANGUAGES}
              values={config.api_languages || ['python']}
              onChange={(v) => updateConfig({ api_languages: v as ('python' | 'node' | 'rust' | 'go')[] })}
            />

            {(config.api_languages?.includes('python') || !config.api_languages) && (
              <FeatureToggleGroup
                label="API Features (Python only)"
                options={API_FEATURES}
                value={config.api_features || 'none'}
                onChange={(v) => updateConfig({ api_features: v as 'none' | 'graphql' | 'websocket' | 'graphql,websocket' })}
              />
            )}
          </div>
        </ModuleCard>

        {/* MCP Module */}
        <ModuleCard
          title="MCP Server"
          description="Model Context Protocol server for AI agent integrations"
          icon={Cpu}
          enabled={config.mcp_module === 'enabled'}
          onToggle={(enabled) => updateConfig({ mcp_module: enabled ? 'enabled' : 'disabled' })}
          accentColor="purple"
        >
          <LanguageSelector
            label="Implementation Languages"
            helperText="(select multiple)"
            options={MCP_LANGUAGES}
            values={config.mcp_languages || ['python']}
            onChange={(v) => updateConfig({ mcp_languages: v as ('python' | 'typescript' | 'rust' | 'go')[] })}
          />
        </ModuleCard>

        {/* Developer Tools Section */}
        <div className="pt-4">
          <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
            Developer Tools
          </h3>

          <div className="space-y-3">
            {/* Codegen Module */}
            <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/30 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Code className="h-5 w-5 text-gray-400" />
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Code Generation</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Jinja2 template rendering utilities</p>
                  </div>
                </div>
                <FeatureToggleGroup
                  label=""
                  options={ENABLE_DISABLE}
                  value={config.codegen_module || 'disabled'}
                  onChange={(v) => updateConfig({ codegen_module: v as 'disabled' | 'enabled' })}
                />
              </div>
            </div>

            {/* Changelog Module */}
            <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/30 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <GitBranch className="h-5 w-5 text-gray-400" />
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Changelog & Releases</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Semantic versioning with git-cliff</p>
                  </div>
                </div>
                <FeatureToggleGroup
                  label=""
                  options={ENABLE_DISABLE}
                  value={config.changelog_module || 'disabled'}
                  onChange={(v) => updateConfig({ changelog_module: v as 'disabled' | 'enabled' })}
                />
              </div>
            </div>

            {/* Shared Logic */}
            <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/30 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Package className="h-5 w-5 text-gray-400" />
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Shared Logic Package</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Cross-component shared utilities</p>
                  </div>
                </div>
                <FeatureToggleGroup
                  label=""
                  options={ENABLE_DISABLE}
                  value={config.shared_logic || 'disabled'}
                  onChange={(v) => updateConfig({ shared_logic: v as 'disabled' | 'enabled' })}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
