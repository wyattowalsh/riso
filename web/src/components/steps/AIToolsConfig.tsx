import { Info } from 'lucide-react'
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

      {/* Enable/Disable Toggle - Master Toggle */}
      <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-riso-teal/10 to-riso-cornflower/10 dark:from-riso-teal/5 dark:to-riso-cornflower/5 border border-riso-teal/20 dark:border-riso-teal/10">
        <div>
          <h3 className="font-semibold text-gray-900 dark:text-white">Enable AI Tools</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Configure MCP servers and AI assistants</p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={isEnabled}
            onChange={(e) => updateConfig({ ai_tools_module: e.target.checked ? 'enabled' : 'disabled' })}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-riso-teal/60 dark:peer-focus:ring-riso-teal/40 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-riso-teal"></div>
        </label>
      </div>

      {isEnabled && (
        <div className="space-y-6">
          {/* Info Callout */}
          <div className="flex items-start gap-3 p-4 rounded-xl bg-riso-cornflower/10 dark:bg-riso-cornflower/5 border border-riso-cornflower/20">
            <Info className="h-5 w-5 text-riso-cornflower flex-shrink-0 mt-0.5" />
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Generates config files for Claude Code, Codex CLI, GitHub Copilot CLI, Cursor CLI, Gemini CLI, Amazon Q CLI, and OpenCode. All tools share <code className="bg-gray-200 dark:bg-gray-800 px-1.5 py-0.5 rounded font-mono text-xs">AGENTS.md</code> as the single source of truth.
            </p>
          </div>

          {/* MCP Servers Section */}
          <div className="riso-card-soft p-5 space-y-4 border border-riso-teal/20 dark:border-riso-teal/10">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-riso-teal"></div>
              <h3 className="font-semibold text-gray-900 dark:text-white text-riso-teal">MCP Servers</h3>
            </div>

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
        </div>
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
    <label className="flex items-start gap-3 p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900/50 cursor-pointer hover:border-riso-teal/50 transition-all hover:-translate-y-0.5 hover:shadow-md">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-0.5 h-4 w-4 rounded border-gray-300 text-riso-teal focus:ring-riso-teal accent-riso-teal"
      />
      <div>
        <div className="font-medium text-sm text-gray-900 dark:text-white">{label}</div>
        <div className="text-xs text-gray-500 dark:text-gray-400">{description}</div>
      </div>
    </label>
  )
}
