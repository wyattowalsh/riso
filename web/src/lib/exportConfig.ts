import { stringify } from 'yaml'
import { validateProjectName } from '../components/steps/ProjectBasics'
import type { RisoConfig } from './store'
import {
  applyThenRejectRemovedKeys,
  REMOVED_ANSWER_KEYS,
} from './removedAnswerKeys'

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
  const infraOn = config.saas_infra_module === 'enabled'

  if (infraOn) {
    assignIfPresent(args, 'saas_runtime', config.saas_runtime)
    assignIfPresent(args, 'saas_hosting', config.saas_hosting)
    assignIfPresent(args, 'saas_database', config.saas_database)
    assignIfPresent(args, 'saas_orm', config.saas_orm)
    assignIfPresent(args, 'saas_cicd', config.saas_cicd)
    assignIfPresent(args, 'saas_admin_dashboard', config.saas_admin_dashboard)
    assignIfPresent(args, 'saas_storage', config.saas_storage)
    assignIfPresent(args, 'saas_ai', config.saas_ai)
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

    const infraKeys = [
      'saas_multi_tenancy_level',
      'saas_tenancy_model',
      'saas_rbac_system',
      'saas_onboarding',
      'saas_notifications',
      'saas_waitlist',
      'saas_search_provider',
      'saas_i18n',
      'saas_api_access',
      'saas_ui_framework',
      'saas_form_library',
      'saas_realtime',
      'saas_landing_page',
      'saas_blog',
      'saas_changelog_public',
      'saas_compliance_level',
      'saas_gdpr_tools',
      'saas_ai_features',
      'saas_rate_limiting',
      'saas_file_upload',
    ] as const
    for (const key of infraKeys) {
      assignIfPresent(args, key, config[key])
    }

    assignIfPresent(args, 'saas_auth_module', config.saas_auth_module)
  }

  if (infraOn && config.saas_auth_module === 'enabled') {
    assignIfPresent(args, 'saas_auth_provider', config.saas_auth_provider)
    assignIfPresent(args, 'saas_enterprise_bridge', config.saas_enterprise_bridge)
    if (config.saas_auth_provider === 'authjs') {
      assignIfPresent(args, 'saas_2fa', config.saas_2fa)
    }
    assignIfPresent(args, 'saas_billing_module', config.saas_billing_module)
  }

  if (
    infraOn &&
    config.saas_auth_module === 'enabled' &&
    config.saas_billing_module === 'enabled'
  ) {
    assignIfPresent(args, 'saas_billing_provider', config.saas_billing_provider)
    assignIfPresent(args, 'saas_app_module', config.saas_app_module)
  }

  if (config.saas_app_module === 'enabled') {
    assignIfPresent(args, 'saas_jobs', config.saas_jobs)
    assignIfPresent(args, 'saas_email', config.saas_email)
    assignIfPresent(args, 'saas_analytics', config.saas_analytics)
    if (config.saas_admin_dashboard) {
      assignIfPresent(args, 'saas_user_impersonation', config.saas_user_impersonation)
    }
    if (config.saas_api_access === 'public-api') {
      assignIfPresent(args, 'saas_api_docs', config.saas_api_docs)
    }
  }

  if (
    infraOn &&
    (config.saas_ai_features === 'rag' || config.saas_ai_features === 'full')
  ) {
    assignIfPresent(args, 'vector_db_provider', config.vector_db_provider)
    if (config.vector_db_provider && config.vector_db_provider !== 'none') {
      assignIfPresent(args, 'embedding_provider', config.embedding_provider)
    }
  }
}

function usesGo(config: Partial<RisoConfig>): boolean {
  return Boolean(
    config.cli_languages?.includes('go') ||
      config.api_languages?.includes('go') ||
      config.mcp_languages?.includes('go'),
  )
}

function assignDesktopGoMcpOptions(
  config: Partial<RisoConfig>,
  args: CopierArgs,
): void {
  assignIfPresent(args, 'desktop_module', config.desktop_module)
  if (config.desktop_module === 'enabled') {
    assignIfPresent(args, 'desktop_framework', config.desktop_framework)
    assignIfPresent(args, 'desktop_features', config.desktop_features)
    assignIfPresent(args, 'desktop_platforms', config.desktop_platforms)
  }

  if (usesGo(config)) {
    assignIfPresent(args, 'go_version', config.go_version)
  }
  if (config.api_module === 'enabled' && config.api_languages?.includes('go')) {
    assignIfPresent(args, 'go_framework', config.go_framework)
  }

  if (config.mcp_module === 'enabled') {
    assignIfPresent(args, 'mcp_transport', config.mcp_transport)
    assignIfPresent(args, 'mcp_example_tools', config.mcp_example_tools)
  }

  if (config.api_module === 'enabled') {
    assignIfPresent(args, 'include_databases', config.include_databases)
  }

  if ((config.ci_platform ?? 'github-actions') === 'github-actions') {
    assignIfPresent(args, 'python_versions', config.python_versions)
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
export function configToCopierArgs(
  config: Partial<RisoConfig> | Record<string, unknown>,
): CopierArgs {
  const remapped = applyThenRejectRemovedKeys({ ...config })
  const src = remapped.answers as Partial<RisoConfig>
  const args: CopierArgs = {}

  // Project basics
  if (src.project_name) args.project_name = src.project_name
  assignIfPresent(args, 'project_layout', src.project_layout)
  assignIfPresent(args, 'quality_profile', src.quality_profile)
  assignIfPresent(args, 'task_runner', src.task_runner)
  assignIfPresent(args, 'openspec_extra', src.openspec_extra)
  assignIfPresent(args, 'ci_platform', src.ci_platform)

  // CLI module
  assignIfPresent(args, 'cli_module', src.cli_module)
  if (src.cli_module === 'enabled' && src.cli_languages?.length) {
    args.cli_languages = src.cli_languages
  }

  // API module
  assignIfPresent(args, 'api_module', src.api_module)
  if (src.api_module === 'enabled') {
    if (src.api_languages?.length) args.api_languages = src.api_languages
    if (src.api_features && src.api_features !== 'none') {
      args.api_features = String(src.api_features)
        .split(',')
        .map((part) => part.trim())
        .filter((part) => part && part !== 'none')
    }
  }

  // MCP module
  assignIfPresent(args, 'mcp_module', src.mcp_module)
  if (src.mcp_module === 'enabled' && src.mcp_languages?.length) {
    args.mcp_languages = src.mcp_languages
  }

  // Documentation module
  assignIfPresent(args, 'docs_module', src.docs_module)
  if (src.docs_module === 'enabled' && src.docs_framework) {
    args.docs_framework = src.docs_framework
  }

  // Shared modules
  assignIfPresent(args, 'codegen_module', src.codegen_module)
  assignIfPresent(args, 'changelog_module', src.changelog_module)
  assignIfPresent(args, 'shared_logic', src.shared_logic)

  assignFumadocsOptions(src, args)
  assignDocusaurusOptions(src, args)
  assignSaasOptions(src, args)
  assignAiToolsOptions(src, args)
  assignDesktopGoMcpOptions(src, args)

  for (const op of remapped.ops) {
    for (const key of op.new_keys) {
      if (key in remapped.answers && remapped.answers[key] !== undefined && !(key in args)) {
        args[key] = remapped.answers[key]
      }
    }
  }
  for (const key of Object.keys(REMOVED_ANSWER_KEYS)) {
    delete args[key]
  }

  return args
}

/** POSIX-safe single-quoted shell literal. */
export function shellEscapeString(value: string): string {
  return `'${value.replace(/'/g, `'\\''`)}'`
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
  const dest = shellEscapeString(`./${projectName}`)
  return [
    `# Download the YAML from this page as copier-answers.yml first.`,
    `uv run riso copy ${dest} --answers-file copier-answers.yml`,
  ].join('\n')
}

export function generateYamlConfig(
  config: Partial<RisoConfig> | Record<string, unknown>,
): string {
  const yamlObj = configToCopierArgs(config)
  const header = `# Riso Configuration
# Generated: ${new Date().toISOString()}
# Usage: uv run riso copy --answers-file copier-answers.yml

`
  return header + stringify(yamlObj)
}

export type GenerateResult =
  | { ok: true; value: string }
  | { ok: false; error: string }

function catchGenerate(err: unknown): GenerateResult {
  return {
    ok: false,
    error: err instanceof Error ? err.message : String(err),
  }
}

/** Soft-fail wrapper so Review cannot crash the wizard on invalid names. */
export function tryGenerateCliCommand(
  config: Partial<RisoConfig>,
): GenerateResult {
  try {
    return { ok: true, value: generateCliCommand(config) }
  } catch (err) {
    return catchGenerate(err)
  }
}

export function tryGenerateYamlConfig(
  config: Partial<RisoConfig> | Record<string, unknown>,
): GenerateResult {
  try {
    return { ok: true, value: generateYamlConfig(config) }
  } catch (err) {
    return catchGenerate(err)
  }
}
