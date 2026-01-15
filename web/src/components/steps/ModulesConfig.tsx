import { useRisoStore } from '../../lib/store'
import { buildChoiceOptions, getPromptHelpSummary } from '../../lib/matrixData'
import { cn } from '../../lib/utils'

interface ToggleOption {
  value: string
  label: string
  description?: string
}

function ToggleGroup({
  label,
  options,
  value,
  onChange,
  disabled = false
}: {
  label: string
  options: ToggleOption[]
  value: string
  onChange: (value: string) => void
  disabled?: boolean
}) {
  return (
    <div className={cn(disabled && 'opacity-50')}>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {label}
      </label>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            disabled={disabled}
            aria-pressed={value === option.value}
            onClick={() => onChange(option.value)}
            className={cn(
              'px-4 py-2 rounded-full text-sm font-semibold transition-all border hover:-translate-y-0.5',
              value === option.value
                ? 'bg-riso-500 text-white border-riso-500 shadow-md shadow-riso-500/30'
                : 'bg-white/80 dark:bg-gray-900/70 text-gray-700 dark:text-gray-300 border-white/70 dark:border-gray-700/60 hover:border-riso-300'
            )}
            title={option.description}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  )
}

export function ModulesConfig() {
  const { config, updateConfig } = useRisoStore()

  const apiTracksOptions: ToggleOption[] = buildChoiceOptions({
    key: 'api_tracks',
    fallbackChoices: ['none', 'python', 'node', 'python+node'],
    labels: {
      none: 'None',
      python: 'Python',
      node: 'Node.js',
      'python+node': 'Both',
    },
    descriptions: {
      none: 'No API scaffolding',
      python: 'FastAPI service',
      node: 'Fastify service',
      'python+node': 'FastAPI + Fastify',
    },
  })

  const enableDisableOptions: ToggleOption[] = buildChoiceOptions({
    key: 'cli_module',
    fallbackChoices: ['disabled', 'enabled'],
    labels: {
      disabled: 'Disabled',
      enabled: 'Enabled',
    },
  })

  const hasPythonAPI = config.api_tracks === 'python' || config.api_tracks === 'python+node'

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-display font-semibold text-gray-900 dark:text-white">Modules</h2>
        <p className="mt-1 text-gray-500 dark:text-gray-400">
          Layer on the capabilities your project actually needs.
        </p>
      </div>

      <div className="grid gap-6">
        {/* API Tracks */}
        <ToggleGroup
          label="API Tracks"
          options={apiTracksOptions}
          value={config.api_tracks || 'none'}
          onChange={(v) => updateConfig({ api_tracks: v as 'none' | 'python' | 'node' | 'python+node' })}
        />
        {getPromptHelpSummary('api_tracks') && (
          <p className="text-xs text-gray-500 -mt-4">{getPromptHelpSummary('api_tracks')}</p>
        )}

        {/* CLI Module */}
        <ToggleGroup
          label="CLI Module (Typer)"
          options={enableDisableOptions}
          value={config.cli_module || 'disabled'}
          onChange={(v) => updateConfig({ cli_module: v as 'disabled' | 'enabled' })}
        />
        {getPromptHelpSummary('cli_module') && (
          <p className="text-xs text-gray-500 -mt-4">{getPromptHelpSummary('cli_module')}</p>
        )}

        {/* GraphQL Module */}
        <ToggleGroup
          label="GraphQL API (Strawberry)"
          options={enableDisableOptions}
          value={config.graphql_api_module || 'disabled'}
          onChange={(v) => updateConfig({ graphql_api_module: v as 'disabled' | 'enabled' })}
          disabled={!hasPythonAPI}
        />
        {!hasPythonAPI && (
          <p className="text-xs text-amber-600 dark:text-amber-400 -mt-4">Requires Python API track</p>
        )}
        {getPromptHelpSummary('graphql_api_module') && (
          <p className="text-xs text-gray-500 -mt-4">{getPromptHelpSummary('graphql_api_module')}</p>
        )}

        {/* WebSocket Module */}
        <ToggleGroup
          label="WebSocket Module"
          options={enableDisableOptions}
          value={config.websocket_module || 'disabled'}
          onChange={(v) => updateConfig({ websocket_module: v as 'disabled' | 'enabled' })}
          disabled={!hasPythonAPI}
        />
        {!hasPythonAPI && (
          <p className="text-xs text-amber-600 dark:text-amber-400 -mt-4">Requires Python API track</p>
        )}
        {getPromptHelpSummary('websocket_module') && (
          <p className="text-xs text-gray-500 -mt-4">{getPromptHelpSummary('websocket_module')}</p>
        )}

        {/* Codegen Module */}
        <ToggleGroup
          label="Codegen Module"
          options={enableDisableOptions}
          value={config.codegen_module || 'disabled'}
          onChange={(v) => updateConfig({ codegen_module: v as 'disabled' | 'enabled' })}
        />
        {getPromptHelpSummary('codegen_module') && (
          <p className="text-xs text-gray-500 -mt-4">{getPromptHelpSummary('codegen_module')}</p>
        )}

        {/* MCP Module */}
        <ToggleGroup
          label="MCP Module (fastmcp)"
          options={enableDisableOptions}
          value={config.mcp_module || 'disabled'}
          onChange={(v) => updateConfig({ mcp_module: v as 'disabled' | 'enabled' })}
        />
        {getPromptHelpSummary('mcp_module') && (
          <p className="text-xs text-gray-500 -mt-4">{getPromptHelpSummary('mcp_module')}</p>
        )}

        {/* Changelog Module */}
        <ToggleGroup
          label="Changelog & Release Management"
          options={enableDisableOptions}
          value={config.changelog_module || 'disabled'}
          onChange={(v) => updateConfig({ changelog_module: v as 'disabled' | 'enabled' })}
        />
        {getPromptHelpSummary('changelog_module') && (
          <p className="text-xs text-gray-500 -mt-4">{getPromptHelpSummary('changelog_module')}</p>
        )}

        {/* Shared Logic */}
        <ToggleGroup
          label="Shared Logic Package"
          options={enableDisableOptions}
          value={config.shared_logic || 'disabled'}
          onChange={(v) => updateConfig({ shared_logic: v as 'disabled' | 'enabled' })}
        />
        {getPromptHelpSummary('shared_logic') && (
          <p className="text-xs text-gray-500 -mt-4">{getPromptHelpSummary('shared_logic')}</p>
        )}
      </div>
    </div>
  )
}
