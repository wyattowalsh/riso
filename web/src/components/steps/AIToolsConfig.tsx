import { useRisoStore } from '../../lib/store'
import { getPromptDefault, getPromptHelpSummary } from '../../lib/matrixData'

export function AIToolsConfig() {
  const { config, updateConfig } = useRisoStore()
  const isEnabled =
    (config.ai_tools_module ??
      getPromptDefault<'enabled' | 'disabled'>('ai_tools_module', 'enabled')) ===
    'enabled'
  const moduleHelp = getPromptHelpSummary('ai_tools_module')

  const thinkingEnabled =
    config.ai_tools_mcp_thinking ?? getPromptDefault<boolean>('ai_tools_mcp_thinking', true) ?? true
  const webEnabled =
    config.ai_tools_mcp_web ?? getPromptDefault<boolean>('ai_tools_mcp_web', true) ?? true
  const docsEnabled =
    config.ai_tools_mcp_documents ?? getPromptDefault<boolean>('ai_tools_mcp_documents', true) ?? true
  const utilitiesEnabled =
    config.ai_tools_mcp_utilities ?? getPromptDefault<boolean>('ai_tools_mcp_utilities', true) ?? true
  const searchEnabled =
    config.ai_tools_mcp_search ?? getPromptDefault<boolean>('ai_tools_mcp_search', false) ?? false

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-display font-semibold text-gray-900 dark:text-white">AI Tools</h2>
        <p className="mt-1 text-gray-500 dark:text-gray-400">
          Enable AI assistants and the MCP servers they rely on.
        </p>
        {moduleHelp && <p className="mt-2 text-xs text-gray-500">{moduleHelp}</p>}
      </div>

      {/* Enable/Disable Toggle */}
      <div className="flex items-center gap-4 p-4 riso-card-soft rounded-xl">
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={isEnabled}
            onChange={(e) => updateConfig({ ai_tools_module: e.target.checked ? 'enabled' : 'disabled' })}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-riso-300/60 dark:peer-focus:ring-riso-800/60 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-riso-500"></div>
        </label>
        <span className="font-medium text-gray-900 dark:text-white">
          {isEnabled ? 'AI Tools Enabled' : 'AI Tools Disabled'}
        </span>
      </div>

      {isEnabled && (
        <>
          <div className="p-4 bg-blue-50/80 dark:bg-blue-900/20 border border-blue-200/80 dark:border-blue-800/60 rounded-xl">
            <p className="text-sm text-blue-700 dark:text-blue-300">
              Generates config files for Claude Code, Codex CLI, GitHub Copilot CLI, Cursor CLI,
              Gemini CLI, Amazon Q CLI, and OpenCode. All tools share <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">AGENTS.md</code> as the single source of truth.
            </p>
          </div>

          <div className="space-y-4">
            <h3 className="font-medium text-gray-900 dark:text-white">MCP Servers</h3>

            <div className="grid gap-4 sm:grid-cols-2">
              <MCPToggle
                label="Thinking/Reasoning"
                description="Sequential, structured, cascade thinking servers"
                checked={thinkingEnabled}
                onChange={(v) => updateConfig({ ai_tools_mcp_thinking: v })}
              />

              <MCPToggle
                label="Web Access"
                description="Fetch, Playwright, DeepWiki for web content"
                checked={webEnabled}
                onChange={(v) => updateConfig({ ai_tools_mcp_web: v })}
              />

              <MCPToggle
                label="Document Processing"
                description="Docling for PDF/DOCX, Repomix for repo context"
                checked={docsEnabled}
                onChange={(v) => updateConfig({ ai_tools_mcp_documents: v })}
              />

              <MCPToggle
                label="Utilities"
                description="Memory persistence and other utilities"
                checked={utilitiesEnabled}
                onChange={(v) => updateConfig({ ai_tools_mcp_utilities: v })}
              />

              <MCPToggle
                label="Search (requires API keys)"
                description="Brave Search, Tavily, Context7"
                checked={searchEnabled}
                onChange={(v) => updateConfig({ ai_tools_mcp_search: v })}
              />
            </div>
          </div>
        </>
      )}
    </div>
  )
}

function MCPToggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string
  description: string
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  return (
    <label className="flex items-start gap-3 p-4 rounded-2xl border border-white/70 dark:border-gray-700/60 bg-white/80 dark:bg-gray-900/70 cursor-pointer hover:border-riso-300 transition-all hover:-translate-y-0.5 hover:shadow-md">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-0.5 h-4 w-4 rounded border-gray-300 text-riso-500 focus:ring-riso-500"
      />
      <div>
        <div className="font-medium text-sm text-gray-900 dark:text-white">{label}</div>
        <div className="text-xs text-gray-500 dark:text-gray-400">{description}</div>
      </div>
    </label>
  )
}
