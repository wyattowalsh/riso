import { stringify } from 'yaml'
import { validateProjectName } from '../components/steps/ProjectBasics'
import type { RisoConfig } from './store'

export type CopierArgs = Record<string, unknown>

function assignIfPresent(
  args: CopierArgs,
  key: keyof RisoConfig,
  value: RisoConfig[keyof RisoConfig] | undefined,
): void {
  if (value !== undefined && value !== null) {
    args[key] = value
  }
}

function assignFumadocsOptions(config: Partial<RisoConfig>, args: CopierArgs): void {
  if (config.docs_module !== 'enabled' || config.docs_framework !== 'fumadocs') {
    return
  }

  const fumadocsKeys: (keyof RisoConfig)[] = [
    'fumadocs_search_provider',
    'fumadocs_llms_txt',
    'fumadocs_ai_search',
    'fumadocs_openapi',
    'fumadocs_typedoc',
    'fumadocs_theme',
    'fumadocs_sidebar',
    'fumadocs_i18n',
    'fumadocs_blog',
    'fumadocs_code_theme',
    'fumadocs_twoslash',
    'fumadocs_image_zoom',
    'fumadocs_banner',
    'fumadocs_last_updated',
    'fumadocs_edit_on_github',
    'fumadocs_feedback',
    'fumadocs_toc_depth',
    'fumadocs_mermaid',
    'fumadocs_math',
  ]

  for (const key of fumadocsKeys) {
    assignIfPresent(args, key, config[key])
  }
}

function assignDocusaurusOptions(config: Partial<RisoConfig>, args: CopierArgs): void {
  if (config.docs_module !== 'enabled' || config.docs_framework !== 'docusaurus') {
    return
  }

  const docusaurusKeys: (keyof RisoConfig)[] = [
    'docusaurus_search_provider',
    'docusaurus_analytics',
    'docusaurus_theme',
    'docusaurus_llms_txt',
    'docusaurus_i18n',
    'docusaurus_versioning',
    'docusaurus_blog',
    'docusaurus_faster',
    'docusaurus_openapi',
    'docusaurus_mermaid',
    'docusaurus_math',
    'docusaurus_live_codeblock',
    'docusaurus_show_last_update',
    'docusaurus_ideal_images',
    'docusaurus_image_zoom',
    'docusaurus_pwa',
    'docusaurus_comments',
    'docusaurus_feedback',
    'docusaurus_sitemap',
    'docusaurus_structured_data',
    'docusaurus_redirects',
    'docusaurus_announcement_bar',
    'docusaurus_back_to_top',
    'docusaurus_edit_url',
    'docusaurus_code_tabs',
    'docusaurus_changelog',
    'docusaurus_debug',
    'docusaurus_reading_time',
    'docusaurus_gfm',
    'docusaurus_emoji',
    'docusaurus_github_links',
    'docusaurus_autolink_headings',
  ]

  for (const key of docusaurusKeys) {
    assignIfPresent(args, key, config[key])
  }
}

function assignSaasOptions(config: Partial<RisoConfig>, args: CopierArgs): void {
  assignIfPresent(args, 'saas_infra_module', config.saas_infra_module)

  if (config.saas_infra_module === 'enabled') {
    assignIfPresent(args, 'saas_runtime', config.saas_runtime)
    assignIfPresent(args, 'saas_hosting', config.saas_hosting)
    assignIfPresent(args, 'saas_database', config.saas_database)
    assignIfPresent(args, 'saas_orm', config.saas_orm)
    assignIfPresent(args, 'saas_cicd', config.saas_cicd)
  }

  assignIfPresent(args, 'saas_auth_module', config.saas_auth_module)
  if (config.saas_auth_module === 'enabled') {
    assignIfPresent(args, 'saas_auth_provider', config.saas_auth_provider)
    assignIfPresent(args, 'saas_enterprise_bridge', config.saas_enterprise_bridge)
  }

  assignIfPresent(args, 'saas_billing_module', config.saas_billing_module)
  if (config.saas_billing_module === 'enabled') {
    assignIfPresent(args, 'saas_billing_provider', config.saas_billing_provider)
  }

  assignIfPresent(args, 'saas_app_module', config.saas_app_module)
  if (config.saas_app_module === 'enabled') {
    assignIfPresent(args, 'saas_jobs', config.saas_jobs)
    assignIfPresent(args, 'saas_email', config.saas_email)
    assignIfPresent(args, 'saas_analytics', config.saas_analytics)
    assignIfPresent(args, 'saas_ai', config.saas_ai)
    assignIfPresent(args, 'saas_storage', config.saas_storage)
    assignIfPresent(args, 'saas_observability_sentry', config.saas_observability_sentry)
    assignIfPresent(args, 'saas_observability_datadog', config.saas_observability_datadog)
    assignIfPresent(args, 'saas_observability_otel', config.saas_observability_otel)
    assignIfPresent(
      args,
      'saas_observability_structured_logging',
      config.saas_observability_structured_logging,
    )
    assignIfPresent(args, 'saas_include_fixtures', config.saas_include_fixtures)
    assignIfPresent(args, 'saas_include_factories', config.saas_include_factories)
    assignIfPresent(args, 'saas_test_suite_level', config.saas_test_suite_level)
  }
}

function assignAiToolsOptions(config: Partial<RisoConfig>, args: CopierArgs): void {
  assignIfPresent(args, 'ai_tools_module', config.ai_tools_module)

  if (config.ai_tools_module !== 'enabled') {
    return
  }

  assignIfPresent(args, 'ai_tools_mcp_thinking', config.ai_tools_mcp_thinking)
  assignIfPresent(args, 'ai_tools_mcp_web', config.ai_tools_mcp_web)
  assignIfPresent(args, 'ai_tools_mcp_documents', config.ai_tools_mcp_documents)
  assignIfPresent(args, 'ai_tools_mcp_utilities', config.ai_tools_mcp_utilities)
  assignIfPresent(args, 'ai_tools_mcp_search', config.ai_tools_mcp_search)
}

/**
 * Map wizard RisoConfig state to Copier answer arguments.
 */
export function configToCopierArgs(config: Partial<RisoConfig>): CopierArgs {
  const args: CopierArgs = {}

  // Project basics
  if (config.project_name) args.project_name = config.project_name
  assignIfPresent(args, 'project_layout', config.project_layout)
  assignIfPresent(args, 'quality_profile', config.quality_profile)
  assignIfPresent(args, 'task_runner', config.task_runner)
  assignIfPresent(args, 'ci_platform', config.ci_platform)

  // CLI module
  assignIfPresent(args, 'cli_module', config.cli_module)
  if (config.cli_module === 'enabled' && config.cli_languages?.length) {
    args.cli_languages = config.cli_languages
  }

  // API module
  assignIfPresent(args, 'api_module', config.api_module)
  if (config.api_module === 'enabled') {
    if (config.api_languages?.length) args.api_languages = config.api_languages
    if (config.api_features && config.api_features !== 'none') {
      args.api_features = config.api_features
    }
  }

  // MCP module
  assignIfPresent(args, 'mcp_module', config.mcp_module)
  if (config.mcp_module === 'enabled' && config.mcp_languages?.length) {
    args.mcp_languages = config.mcp_languages
  }

  // Documentation module
  assignIfPresent(args, 'docs_module', config.docs_module)
  if (config.docs_module === 'enabled' && config.docs_framework) {
    args.docs_framework = config.docs_framework
  }

  // Shared modules
  assignIfPresent(args, 'codegen_module', config.codegen_module)
  assignIfPresent(args, 'changelog_module', config.changelog_module)
  assignIfPresent(args, 'shared_logic', config.shared_logic)

  assignFumadocsOptions(config, args)
  assignDocusaurusOptions(config, args)
  assignSaasOptions(config, args)
  assignAiToolsOptions(config, args)

  return args
}

/** POSIX-safe single-quoted shell literal. */
export function shellEscapeString(value: string): string {
  return `'${value.replace(/'/g, `'\\''`)}'`
}

function formatCliArg(key: string, value: unknown): string {
  if (Array.isArray(value)) {
    return `${key}=${shellEscapeString(JSON.stringify(value))}`
  }
  if (typeof value === 'boolean') {
    return `${key}=${value}`
  }
  if (typeof value === 'string') {
    return `${key}=${shellEscapeString(value)}`
  }
  return `${key}=${shellEscapeString(String(value))}`
}

export function resolveExportProjectName(config: Partial<RisoConfig>): string {
  const candidate = (config.project_name || 'my-project').trim()
  const validation = validateProjectName(candidate)
  if (!validation.valid) {
    throw new Error(validation.error ?? 'Invalid project name for export')
  }
  return candidate
}

export function generateCliCommand(config: Partial<RisoConfig>): string {
  const projectName = resolveExportProjectName(config)
  const args = configToCopierArgs(config)
  if (!args.project_name) {
    args.project_name = projectName
  }
  const dataArgs = Object.entries(args)
    .map(([key, value]) => `  --data ${formatCliArg(key, value)}`)
    .join(' \\\n')

  const dest = shellEscapeString(`./${projectName}`)
  return `uv run riso copy ${dest} \\\n${dataArgs}`
}

export function generateYamlConfig(config: Partial<RisoConfig>): string {
  const yamlObj = configToCopierArgs(config)
  const header = `# Riso Configuration
# Generated: ${new Date().toISOString()}
# Usage: copier copy gh:wyattowalsh/riso . --answers-file copier-answers.yml

`
  return header + stringify(yamlObj)
}
