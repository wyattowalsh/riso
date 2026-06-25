import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { matrixDefaults } from './matrixData'

// Configuration interface aligned with template/copier.yml v2.0 (component-first)
export interface RisoConfig {
  // Project basics
  project_name: string
  project_layout: 'single-package' | 'monorepo'
  quality_profile: 'standard' | 'strict'

  // ========================================
  // Component-First Modules
  // Each component has its own language selector
  // ========================================

  // CLI Module
  cli_module: 'disabled' | 'enabled'
  cli_languages: ('python' | 'rust' | 'go' | 'typescript')[]

  // API Module
  api_module: 'disabled' | 'enabled'
  api_languages: ('python' | 'node' | 'rust' | 'go')[]
  api_features: 'none' | 'graphql' | 'websocket' | 'graphql,websocket'

  // MCP Module
  mcp_module: 'disabled' | 'enabled'
  mcp_languages: ('python' | 'typescript' | 'rust' | 'go')[]

  // Documentation Module
  docs_module: 'disabled' | 'enabled'
  docs_framework: 'fumadocs' | 'sphinx-shibuya' | 'docusaurus' | 'mkdocs'

  // Shared/Utility Modules
  codegen_module: 'disabled' | 'enabled'
  changelog_module: 'disabled' | 'enabled'
  shared_logic: 'disabled' | 'enabled'

  // Fumadocs options
  fumadocs_search_provider: 'orama' | 'algolia' | 'orama-cloud' | 'none'
  fumadocs_llms_txt: 'enabled' | 'disabled'
  fumadocs_ai_search: 'enabled' | 'disabled'
  fumadocs_openapi: 'enabled' | 'disabled'
  fumadocs_typedoc: 'enabled' | 'disabled'
  fumadocs_theme: 'default' | 'shadcn' | 'ocean' | 'purple' | 'custom'
  fumadocs_sidebar: 'default' | 'shadcn'
  fumadocs_i18n: 'enabled' | 'disabled'
  fumadocs_blog: 'enabled' | 'disabled'
  fumadocs_code_theme: 'github' | 'catppuccin' | 'dracula' | 'nord' | 'one'
  fumadocs_twoslash: 'enabled' | 'disabled'
  fumadocs_image_zoom: 'enabled' | 'disabled'
  fumadocs_banner: 'enabled' | 'disabled'
  fumadocs_last_updated: 'enabled' | 'disabled'
  fumadocs_edit_on_github: 'enabled' | 'disabled'
  fumadocs_feedback: 'enabled' | 'disabled'
  fumadocs_toc_depth: '2' | '3' | '4'
  fumadocs_mermaid: 'enabled' | 'disabled'
  fumadocs_math: 'enabled' | 'disabled'

  // Docusaurus options
  docusaurus_search_provider: 'local' | 'algolia' | 'typesense' | 'none'
  docusaurus_analytics: 'none' | 'posthog' | 'google' | 'matomo'
  docusaurus_theme: 'classic' | 'tailwind'
  docusaurus_llms_txt: 'enabled' | 'disabled'
  docusaurus_i18n: 'enabled' | 'disabled'
  docusaurus_versioning: 'enabled' | 'disabled'
  docusaurus_blog: 'enabled' | 'disabled'
  docusaurus_faster: 'enabled' | 'disabled'
  docusaurus_openapi: 'enabled' | 'disabled'
  docusaurus_mermaid: 'enabled' | 'disabled'
  docusaurus_math: 'enabled' | 'disabled'
  docusaurus_live_codeblock: 'enabled' | 'disabled'
  docusaurus_show_last_update: 'enabled' | 'disabled'
  docusaurus_ideal_images: 'enabled' | 'disabled'
  docusaurus_image_zoom: 'enabled' | 'disabled'
  docusaurus_pwa: 'enabled' | 'disabled'
  docusaurus_comments: 'giscus' | 'none'
  docusaurus_feedback: 'enabled' | 'disabled'
  docusaurus_sitemap: 'enabled' | 'disabled'
  docusaurus_structured_data: 'enabled' | 'disabled'
  docusaurus_redirects: 'enabled' | 'disabled'
  docusaurus_announcement_bar: 'enabled' | 'disabled'
  docusaurus_back_to_top: 'enabled' | 'disabled'
  docusaurus_edit_url: 'enabled' | 'disabled'
  docusaurus_code_tabs: 'enabled' | 'disabled'
  docusaurus_changelog: 'enabled' | 'disabled'
  docusaurus_debug: 'enabled' | 'disabled'
  docusaurus_reading_time: 'enabled' | 'disabled'
  docusaurus_gfm: 'enabled' | 'disabled'
  docusaurus_emoji: 'enabled' | 'disabled'
  docusaurus_github_links: 'enabled' | 'disabled'
  docusaurus_autolink_headings: 'enabled' | 'disabled'

  // Infrastructure
  ci_platform: 'github-actions' | 'gitlab-ci' | 'circleci' | 'none'

  // AI Tools
  ai_tools_module: 'enabled' | 'disabled'
  ai_tools_mcp_thinking: boolean
  ai_tools_mcp_web: boolean
  ai_tools_mcp_documents: boolean
  ai_tools_mcp_utilities: boolean
  ai_tools_mcp_search: boolean

  // ========================================
  // SaaS Modular Architecture
  // Layered: infra → auth → billing → app
  // ========================================

  // SaaS Infrastructure Layer (base)
  saas_infra_module: 'enabled' | 'disabled'
  saas_runtime: 'nextjs-16' | 'remix-2'
  saas_hosting: 'vercel' | 'cloudflare'
  saas_database: 'neon' | 'supabase'
  saas_orm: 'prisma' | 'drizzle'
  saas_cicd: 'github-actions' | 'cloudflare-ci'

  // SaaS Auth Layer (requires infra)
  saas_auth_module: 'enabled' | 'disabled'
  saas_auth_provider: 'clerk' | 'authjs' | 'lucia'
  saas_enterprise_bridge: 'workos' | 'none'

  // SaaS Billing Layer (requires auth)
  saas_billing_module: 'enabled' | 'disabled'
  saas_billing_provider: 'stripe' | 'paddle' | 'lemonsqueezy'

  // SaaS App Layer (requires billing)
  saas_app_module: 'enabled' | 'disabled'
  saas_jobs: 'triggerdev' | 'inngest'
  saas_email: 'resend' | 'postmark'
  saas_analytics: 'posthog' | 'amplitude'
  saas_ai: 'openai' | 'anthropic'
  saas_storage: 'r2' | 'supabase-storage'

  // SaaS Observability
  saas_observability_sentry: boolean
  saas_observability_datadog: boolean
  saas_observability_otel: boolean
  saas_observability_structured_logging: boolean

  // SaaS Testing
  saas_include_fixtures: boolean
  saas_include_factories: boolean
  saas_test_suite_level: 'standard' | 'comprehensive'
}

export interface ConfigHistory {
  id: string
  name: string
  config: Partial<RisoConfig>
  timestamp: Date
}

export interface RisoStore {
  config: Partial<RisoConfig>
  history: ConfigHistory[]
  currentStep: number
  highlightedField: string | null
  isDrawerOpen: boolean

  // Actions
  updateConfig: (config: Partial<RisoConfig>) => void
  resetConfig: () => void
  setStep: (step: number) => void
  setCurrentStep: (step: number) => void // Alias for setStep
  setHighlightedField: (field: string | null) => void
  setDrawerOpen: (isOpen: boolean) => void
  toggleDrawer: () => void
  saveToHistory: (name: string) => void
  loadFromHistory: (id: string) => void
  deleteFromHistory: (id: string) => void
}

const fromMatrix = <T>(key: keyof RisoConfig, fallback: T): T => {
  const value = matrixDefaults?.[key as string]
  if (value === undefined || value === null) {
    return fallback
  }
  return value as T
}

const defaultConfig: Partial<RisoConfig> = {
  // Project basics
  project_name: '',
  project_layout: fromMatrix('project_layout', 'single-package'),
  quality_profile: fromMatrix('quality_profile', 'standard'),

  // ========================================
  // Component-First Module Defaults
  // ========================================

  // CLI Module
  cli_module: fromMatrix('cli_module', 'disabled'),
  cli_languages: fromMatrix('cli_languages', ['python']),

  // API Module
  api_module: fromMatrix('api_module', 'disabled'),
  api_languages: fromMatrix('api_languages', ['python']),
  api_features: fromMatrix('api_features', 'none'),

  // MCP Module
  mcp_module: fromMatrix('mcp_module', 'disabled'),
  mcp_languages: fromMatrix('mcp_languages', ['python']),

  // Documentation Module
  docs_module: fromMatrix('docs_module', 'disabled'),
  docs_framework: fromMatrix('docs_framework', 'fumadocs'),

  // Shared Modules
  codegen_module: fromMatrix('codegen_module', 'disabled'),
  changelog_module: fromMatrix('changelog_module', 'disabled'),
  shared_logic: fromMatrix('shared_logic', 'disabled'),

  // Fumadocs defaults
  fumadocs_search_provider: fromMatrix('fumadocs_search_provider', 'orama'),
  fumadocs_llms_txt: fromMatrix('fumadocs_llms_txt', 'enabled'),
  fumadocs_ai_search: fromMatrix('fumadocs_ai_search', 'disabled'),
  fumadocs_openapi: fromMatrix('fumadocs_openapi', 'enabled'),
  fumadocs_typedoc: fromMatrix('fumadocs_typedoc', 'disabled'),
  fumadocs_theme: fromMatrix('fumadocs_theme', 'shadcn'),
  fumadocs_sidebar: fromMatrix('fumadocs_sidebar', 'default'),
  fumadocs_i18n: fromMatrix('fumadocs_i18n', 'disabled'),
  fumadocs_blog: fromMatrix('fumadocs_blog', 'disabled'),
  fumadocs_code_theme: fromMatrix('fumadocs_code_theme', 'github'),
  fumadocs_twoslash: fromMatrix('fumadocs_twoslash', 'disabled'),
  fumadocs_image_zoom: fromMatrix('fumadocs_image_zoom', 'enabled'),
  fumadocs_banner: fromMatrix('fumadocs_banner', 'disabled'),
  fumadocs_last_updated: fromMatrix('fumadocs_last_updated', 'enabled'),
  fumadocs_edit_on_github: fromMatrix('fumadocs_edit_on_github', 'enabled'),
  fumadocs_feedback: fromMatrix('fumadocs_feedback', 'disabled'),
  fumadocs_toc_depth: fromMatrix('fumadocs_toc_depth', '3'),
  fumadocs_mermaid: fromMatrix('fumadocs_mermaid', 'disabled'),
  fumadocs_math: fromMatrix('fumadocs_math', 'disabled'),

  // Docusaurus defaults
  docusaurus_search_provider: fromMatrix('docusaurus_search_provider', 'local'),
  docusaurus_analytics: fromMatrix('docusaurus_analytics', 'none'),
  docusaurus_theme: fromMatrix('docusaurus_theme', 'classic'),
  docusaurus_llms_txt: fromMatrix('docusaurus_llms_txt', 'enabled'),
  docusaurus_i18n: fromMatrix('docusaurus_i18n', 'disabled'),
  docusaurus_versioning: fromMatrix('docusaurus_versioning', 'disabled'),
  docusaurus_blog: fromMatrix('docusaurus_blog', 'enabled'),
  docusaurus_faster: fromMatrix('docusaurus_faster', 'enabled'),
  docusaurus_openapi: fromMatrix('docusaurus_openapi', 'enabled'),
  docusaurus_mermaid: fromMatrix('docusaurus_mermaid', 'enabled'),
  docusaurus_math: fromMatrix('docusaurus_math', 'disabled'),
  docusaurus_live_codeblock: fromMatrix('docusaurus_live_codeblock', 'disabled'),
  docusaurus_show_last_update: fromMatrix('docusaurus_show_last_update', 'enabled'),
  docusaurus_ideal_images: fromMatrix('docusaurus_ideal_images', 'enabled'),
  docusaurus_image_zoom: fromMatrix('docusaurus_image_zoom', 'disabled'),
  docusaurus_pwa: fromMatrix('docusaurus_pwa', 'disabled'),
  docusaurus_comments: fromMatrix('docusaurus_comments', 'none'),
  docusaurus_feedback: fromMatrix('docusaurus_feedback', 'disabled'),
  docusaurus_sitemap: fromMatrix('docusaurus_sitemap', 'enabled'),
  docusaurus_structured_data: fromMatrix('docusaurus_structured_data', 'disabled'),
  docusaurus_redirects: fromMatrix('docusaurus_redirects', 'disabled'),
  docusaurus_announcement_bar: fromMatrix('docusaurus_announcement_bar', 'disabled'),
  docusaurus_back_to_top: fromMatrix('docusaurus_back_to_top', 'enabled'),
  docusaurus_edit_url: fromMatrix('docusaurus_edit_url', 'enabled'),
  docusaurus_code_tabs: fromMatrix('docusaurus_code_tabs', 'disabled'),
  docusaurus_changelog: fromMatrix('docusaurus_changelog', 'disabled'),
  docusaurus_debug: fromMatrix('docusaurus_debug', 'disabled'),
  docusaurus_reading_time: fromMatrix('docusaurus_reading_time', 'enabled'),
  docusaurus_gfm: fromMatrix('docusaurus_gfm', 'enabled'),
  docusaurus_emoji: fromMatrix('docusaurus_emoji', 'disabled'),
  docusaurus_github_links: fromMatrix('docusaurus_github_links', 'disabled'),
  docusaurus_autolink_headings: fromMatrix('docusaurus_autolink_headings', 'enabled'),

  // Infrastructure
  ci_platform: fromMatrix('ci_platform', 'github-actions'),

  // AI Tools
  ai_tools_module: fromMatrix('ai_tools_module', 'enabled'),
  ai_tools_mcp_thinking: fromMatrix('ai_tools_mcp_thinking', true),
  ai_tools_mcp_web: fromMatrix('ai_tools_mcp_web', true),
  ai_tools_mcp_documents: fromMatrix('ai_tools_mcp_documents', true),
  ai_tools_mcp_utilities: fromMatrix('ai_tools_mcp_utilities', true),
  ai_tools_mcp_search: fromMatrix('ai_tools_mcp_search', false),

  // ========================================
  // SaaS Modular Architecture Defaults
  // ========================================

  // SaaS Infrastructure Layer
  saas_infra_module: fromMatrix('saas_infra_module', 'disabled'),
  saas_runtime: fromMatrix('saas_runtime', 'nextjs-16'),
  saas_hosting: fromMatrix('saas_hosting', 'vercel'),
  saas_database: fromMatrix('saas_database', 'neon'),
  saas_orm: fromMatrix('saas_orm', 'prisma'),
  saas_cicd: fromMatrix('saas_cicd', 'github-actions'),

  // SaaS Auth Layer
  saas_auth_module: fromMatrix('saas_auth_module', 'disabled'),
  saas_auth_provider: fromMatrix('saas_auth_provider', 'clerk'),
  saas_enterprise_bridge: fromMatrix('saas_enterprise_bridge', 'none'),

  // SaaS Billing Layer
  saas_billing_module: fromMatrix('saas_billing_module', 'disabled'),
  saas_billing_provider: fromMatrix('saas_billing_provider', 'stripe'),

  // SaaS App Layer
  saas_app_module: fromMatrix('saas_app_module', 'disabled'),
  saas_jobs: fromMatrix('saas_jobs', 'triggerdev'),
  saas_email: fromMatrix('saas_email', 'resend'),
  saas_analytics: fromMatrix('saas_analytics', 'posthog'),
  saas_ai: fromMatrix('saas_ai', 'openai'),
  saas_storage: fromMatrix('saas_storage', 'r2'),

  // SaaS Observability
  saas_observability_sentry: fromMatrix('saas_observability_sentry', true),
  saas_observability_datadog: fromMatrix('saas_observability_datadog', true),
  saas_observability_otel: fromMatrix('saas_observability_otel', true),
  saas_observability_structured_logging: fromMatrix('saas_observability_structured_logging', true),

  // SaaS Testing
  saas_include_fixtures: fromMatrix('saas_include_fixtures', true),
  saas_include_factories: fromMatrix('saas_include_factories', true),
  saas_test_suite_level: fromMatrix('saas_test_suite_level', 'standard'),
}

export const useRisoStore = create<RisoStore>()(
  persist(
    (set, get) => ({
      config: defaultConfig,
      history: [],
      currentStep: 0,
      highlightedField: null,
      isDrawerOpen: false,

      updateConfig: (config) =>
        set((state) => ({
          config: { ...state.config, ...config },
        })),

      resetConfig: () =>
        set({
          config: defaultConfig,
          currentStep: 0,
        }),

      setStep: (step) =>
        set({ currentStep: step }),

      setCurrentStep: (step) =>
        set({ currentStep: step }),

      setHighlightedField: (field) =>
        set({ highlightedField: field }),

      setDrawerOpen: (isOpen) =>
        set({ isDrawerOpen: isOpen }),

      toggleDrawer: () =>
        set((state) => ({ isDrawerOpen: !state.isDrawerOpen })),

      saveToHistory: (name) =>
        set((state) => ({
          history: [
            {
              id: crypto.randomUUID(),
              name,
              config: state.config,
              timestamp: new Date(),
            },
            ...state.history,
          ].slice(0, 10), // Keep last 10
        })),

      loadFromHistory: (id) => {
        const history = get().history.find((h) => h.id === id)
        if (history) {
          set({ config: history.config })
        }
      },

      deleteFromHistory: (id) =>
        set((state) => ({
          history: state.history.filter((h) => h.id !== id),
        })),
    }),
    {
      name: 'riso-config-storage',
      storage: createJSONStorage(() => localStorage),
      // Don't persist UI state like drawer open/closed
      partialize: (state) => ({
        config: state.config,
        history: state.history,
        currentStep: state.currentStep,
        highlightedField: state.highlightedField,
      }),
    }
  )
)
