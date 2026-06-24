/**
 * Search Engine for Riso Configuration Options
 *
 * Provides fuzzy search across all configuration options with:
 * - Key matching (e.g., "fumadocs" matches fumadocs_*)
 * - Label matching (e.g., "search" matches search providers)
 * - Description matching (e.g., "mermaid" matches diagram options)
 */

import type { RisoConfig } from './store'
import { getPrompt, getPromptHelpSummary, formatChoiceLabel } from './matrixData'

export interface SearchableOption {
  key: keyof RisoConfig
  label: string
  description: string
  category: string
  step: number
  keywords: string[]
}

export interface SearchResult {
  option: SearchableOption
  score: number
  matches: {
    key?: boolean
    label?: boolean
    description?: boolean
    keywords?: boolean
  }
}

// Map config keys to wizard steps
const STEP_MAP: Record<string, number> = {
  // Step 0: Project Basics
  project_name: 0,
  project_layout: 0,
  quality_profile: 0,

  // Step 1: Modules
  cli_module: 1,
  cli_languages: 1,
  api_module: 1,
  api_languages: 1,
  api_features: 1,
  mcp_module: 1,
  mcp_languages: 1,
  docs_module: 1,
  docs_framework: 1,
  codegen_module: 1,
  changelog_module: 1,
  shared_logic: 1,

  // Step 2: Docs Config (all fumadocs_* and docusaurus_*)
  // Auto-detected below

  // Step 3: SaaS Config (all saas_*)
  // Auto-detected below

  // Step 4: AI Tools
  ai_tools_module: 4,
  ai_tools_mcp_thinking: 4,
  ai_tools_mcp_web: 4,
  ai_tools_mcp_documents: 4,
  ai_tools_mcp_utilities: 4,
  ai_tools_mcp_search: 4,

  // Step 5: Review
  ci_platform: 0,
}

// Category labels
const CATEGORY_MAP: Record<string, string> = {
  project: 'Project',
  cli: 'CLI',
  api: 'API',
  mcp: 'MCP',
  docs: 'Documentation',
  fumadocs: 'Fumadocs',
  docusaurus: 'Docusaurus',
  saas: 'SaaS',
  ai: 'AI Tools',
  ci: 'CI/CD',
  quality: 'Quality',
  codegen: 'Codegen',
  changelog: 'Changelog',
  shared: 'Shared Logic',
}

// Additional keywords for better matching
const EXTRA_KEYWORDS: Record<string, string[]> = {
  fumadocs_mermaid: ['diagram', 'flowchart', 'chart', 'visualization'],
  fumadocs_math: ['latex', 'equation', 'formula', 'katex'],
  fumadocs_twoslash: ['typescript', 'hover', 'type hints'],
  fumadocs_blog: ['posts', 'articles', 'blog posts'],
  docusaurus_mermaid: ['diagram', 'flowchart', 'chart', 'visualization'],
  docusaurus_math: ['latex', 'equation', 'formula', 'katex'],
  docusaurus_pwa: ['offline', 'progressive web app', 'service worker'],
  saas_auth_provider: ['login', 'authentication', 'oauth', 'sso'],
  saas_billing_provider: ['payments', 'subscriptions', 'stripe', 'checkout'],
  saas_analytics: ['tracking', 'metrics', 'posthog', 'google analytics'],
  saas_email: ['notifications', 'transactional', 'resend', 'postmark'],
  api_features: ['graphql', 'websocket', 'realtime', 'subscriptions'],
  cli_languages: ['terminal', 'command line', 'clap', 'typer'],
  mcp_languages: ['model context protocol', 'llm tools', 'ai tools'],
}

// Build searchable options from config interface
export function buildSearchIndex(): SearchableOption[] {
  const options: SearchableOption[] = []

  // Get all keys from a sample config
  const sampleKeys: (keyof RisoConfig)[] = [
    'project_name',
    'project_layout',
    'quality_profile',
    'cli_module',
    'cli_languages',
    'api_module',
    'api_languages',
    'api_features',
    'mcp_module',
    'mcp_languages',
    'docs_module',
    'docs_framework',
    'codegen_module',
    'changelog_module',
    'shared_logic',
    'ci_platform',
    'ai_tools_module',
  ]

  // Add fumadocs options
  const fumadocsKeys = [
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
  ] as const

  // Add docusaurus options
  const docusaurusKeys = [
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
    'docusaurus_pwa',
    'docusaurus_comments',
    'docusaurus_feedback',
  ] as const

  // Add SaaS options
  const saasKeys = [
    'saas_infra_module',
    'saas_runtime',
    'saas_hosting',
    'saas_database',
    'saas_orm',
    'saas_auth_module',
    'saas_auth_provider',
    'saas_enterprise_bridge',
    'saas_billing_module',
    'saas_billing_provider',
    'saas_app_module',
    'saas_jobs',
    'saas_email',
    'saas_analytics',
    'saas_ai',
    'saas_storage',
  ] as const

  // Add AI tools options
  const aiToolsKeys = [
    'ai_tools_mcp_thinking',
    'ai_tools_mcp_web',
    'ai_tools_mcp_documents',
    'ai_tools_mcp_utilities',
    'ai_tools_mcp_search',
  ] as const

  const allKeys = [
    ...sampleKeys,
    ...fumadocsKeys,
    ...docusaurusKeys,
    ...saasKeys,
    ...aiToolsKeys,
  ] as (keyof RisoConfig)[]

  for (const key of allKeys) {
    const prompt = getPrompt(key)
    const helpText = getPromptHelpSummary(key)

    // Determine step
    let step = STEP_MAP[key] ?? -1
    if (step === -1) {
      if (key.startsWith('fumadocs_') || key.startsWith('docusaurus_')) {
        step = 2
      } else if (key.startsWith('saas_')) {
        step = 3
      }
    }

    // Determine category
    let category = 'Other'
    const prefix = key.split('_')[0]
    if (CATEGORY_MAP[prefix]) {
      category = CATEGORY_MAP[prefix]
    }

    // Build label from key
    const label = formatChoiceLabel(
      key
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase())
    )

    // Build keywords
    const keywords: string[] = [
      ...key.split('_'),
      ...(EXTRA_KEYWORDS[key] || []),
    ]

    if (prompt?.help) {
      // Extract words from help text
      const helpWords = prompt.help
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, '')
        .split(/\s+/)
        .filter((w) => w.length > 3)
      keywords.push(...helpWords)
    }

    options.push({
      key,
      label,
      description: helpText || `Configure ${label}`,
      category,
      step,
      keywords: [...new Set(keywords)],
    })
  }

  return options
}

// Fuzzy search scoring
function fuzzyScore(query: string, text: string): number {
  const lowerQuery = query.toLowerCase()
  const lowerText = text.toLowerCase()

  // Exact match
  if (lowerText === lowerQuery) return 100

  // Starts with
  if (lowerText.startsWith(lowerQuery)) return 90

  // Contains
  if (lowerText.includes(lowerQuery)) return 70

  // Fuzzy character matching
  let score = 0
  let queryIndex = 0
  for (let i = 0; i < lowerText.length && queryIndex < lowerQuery.length; i++) {
    if (lowerText[i] === lowerQuery[queryIndex]) {
      score += 10
      queryIndex++
    }
  }

  // Penalize if not all characters matched
  if (queryIndex < lowerQuery.length) {
    score = Math.max(0, score - (lowerQuery.length - queryIndex) * 5)
  }

  return Math.min(score, 60) // Cap fuzzy matches
}

// Search function
export function searchOptions(
  query: string,
  index: SearchableOption[]
): SearchResult[] {
  if (!query || query.length < 2) return []

  const results: SearchResult[] = []
  const lowerQuery = query.toLowerCase()

  for (const option of index) {
    let maxScore = 0
    const matches: SearchResult['matches'] = {}

    // Score key match
    const keyScore = fuzzyScore(lowerQuery, option.key)
    if (keyScore > 0) {
      maxScore = Math.max(maxScore, keyScore)
      matches.key = true
    }

    // Score label match
    const labelScore = fuzzyScore(lowerQuery, option.label)
    if (labelScore > 0) {
      maxScore = Math.max(maxScore, labelScore)
      matches.label = true
    }

    // Score description match
    const descScore = fuzzyScore(lowerQuery, option.description)
    if (descScore > 0) {
      maxScore = Math.max(maxScore, descScore * 0.8) // Slightly lower weight
      matches.description = true
    }

    // Score keyword matches
    for (const keyword of option.keywords) {
      const kwScore = fuzzyScore(lowerQuery, keyword)
      if (kwScore > 0) {
        maxScore = Math.max(maxScore, kwScore * 0.6)
        matches.keywords = true
      }
    }

    if (maxScore > 20) {
      results.push({
        option,
        score: maxScore,
        matches,
      })
    }
  }

  // Sort by score descending
  return results.sort((a, b) => b.score - a.score).slice(0, 15)
}

// Step names for navigation
export const STEP_NAMES = [
  'Project Basics',
  'Modules',
  'Documentation',
  'SaaS',
  'AI Tools',
  'Review',
]

// Get suggested searches based on common queries
export const SUGGESTED_SEARCHES = [
  { query: 'search', description: 'Search providers and options' },
  { query: 'auth', description: 'Authentication options' },
  { query: 'database', description: 'Database and ORM options' },
  { query: 'analytics', description: 'Analytics integrations' },
  { query: 'blog', description: 'Blog functionality' },
  { query: 'mermaid', description: 'Diagram support' },
  { query: 'graphql', description: 'GraphQL API options' },
]

// Documentation links for search
export const DOC_ENTRIES = [
  { title: 'Quickstart Guide', url: '/docs/guides/quickstart.html', keywords: ['start', 'begin', 'setup', 'install'] },
  { title: 'MCP Server', url: '/docs/tools/riso-mcp-server.html', keywords: ['mcp', 'model context', 'tools'] },
  { title: 'Testing Strategy', url: '/docs/guides/testing-strategy.html', keywords: ['test', 'quality', 'ci'] },
  { title: 'Matrix Data', url: '/docs/guides/matrix-data.html', keywords: ['matrix', 'options', 'config'] },
  { title: 'Troubleshooting', url: '/docs/guides/troubleshooting.html', keywords: ['error', 'fix', 'problem', 'help'] },
  { title: 'CI Platforms', url: '/docs/guides/ci-platforms.html', keywords: ['github', 'gitlab', 'ci', 'actions'] },
  { title: 'API Reference', url: '/docs/api/index.html', keywords: ['api', 'reference', 'module'] },
]
