/**
 * Dependency Engine for Riso Configuration
 *
 * Defines and validates dependencies between configuration options.
 * Supports:
 * - Requirements: Option A requires Option B to be enabled
 * - Conflicts: Option A cannot be used with Option B
 * - Recommendations: Option A works best with Option B
 */

import type { RisoConfig } from './store'

// Dependency types
export type DependencyType = 'requires' | 'conflicts' | 'recommends'

export interface Dependency {
  type: DependencyType
  source: keyof RisoConfig
  sourceValue?: string | boolean
  target: keyof RisoConfig
  targetValue?: string | boolean
  message: string
}

export interface DependencyWarning {
  type: 'error' | 'warning' | 'info'
  field: keyof RisoConfig
  message: string
  relatedField?: keyof RisoConfig
}

// Define all dependency rules
export const DEPENDENCY_RULES: Dependency[] = [
  // ========================================
  // SaaS Layer Dependencies (infra → auth → billing → app)
  // ========================================
  {
    type: 'requires',
    source: 'saas_auth_module',
    sourceValue: 'enabled',
    target: 'saas_infra_module',
    targetValue: 'enabled',
    message: 'Auth layer requires Infrastructure layer to be enabled',
  },
  {
    type: 'requires',
    source: 'saas_billing_module',
    sourceValue: 'enabled',
    target: 'saas_auth_module',
    targetValue: 'enabled',
    message: 'Billing layer requires Auth layer to be enabled',
  },
  {
    type: 'requires',
    source: 'saas_app_module',
    sourceValue: 'enabled',
    target: 'saas_infra_module',
    targetValue: 'enabled',
    message: 'Application layer requires Infrastructure layer to be enabled',
  },

  // ========================================
  // Docs Framework Dependencies
  // ========================================
  {
    type: 'requires',
    source: 'fumadocs_openapi',
    sourceValue: 'enabled',
    target: 'api_module',
    targetValue: 'enabled',
    message: 'OpenAPI docs require an API module to be enabled',
  },
  {
    type: 'requires',
    source: 'docusaurus_openapi',
    sourceValue: 'enabled',
    target: 'api_module',
    targetValue: 'enabled',
    message: 'OpenAPI docs require an API module to be enabled',
  },

  // ========================================
  // API Feature Dependencies
  // ========================================
  {
    type: 'recommends',
    source: 'api_features',
    sourceValue: 'graphql',
    target: 'api_languages',
    // Note: For array fields, this recommendation suggests Python should be included
    message: 'GraphQL works best with Python API (Strawberry)',
  },

  // ========================================
  // AI Tools Dependencies
  // ========================================
  {
    type: 'requires',
    source: 'ai_tools_mcp_thinking',
    sourceValue: true,
    target: 'ai_tools_module',
    targetValue: 'enabled',
    message: 'MCP Thinking requires AI Tools module to be enabled',
  },
  {
    type: 'requires',
    source: 'ai_tools_mcp_web',
    sourceValue: true,
    target: 'ai_tools_module',
    targetValue: 'enabled',
    message: 'MCP Web requires AI Tools module to be enabled',
  },
  {
    type: 'requires',
    source: 'ai_tools_mcp_documents',
    sourceValue: true,
    target: 'ai_tools_module',
    targetValue: 'enabled',
    message: 'MCP Documents requires AI Tools module to be enabled',
  },
  {
    type: 'requires',
    source: 'ai_tools_mcp_utilities',
    sourceValue: true,
    target: 'ai_tools_module',
    targetValue: 'enabled',
    message: 'MCP Utilities requires AI Tools module to be enabled',
  },
  {
    type: 'requires',
    source: 'ai_tools_mcp_search',
    sourceValue: true,
    target: 'ai_tools_module',
    targetValue: 'enabled',
    message: 'MCP Search requires AI Tools module to be enabled',
  },

  // ========================================
  // MCP Language Recommendations
  // ========================================
  {
    type: 'recommends',
    source: 'mcp_languages',
    // Note: Recommendation applies when Python is in mcp_languages
    target: 'api_languages',
    // Note: For array fields, this recommendation suggests Python should be included in both
    message: 'Using Python for both MCP and API enables code sharing',
  },

  // ========================================
  // Search Provider Dependencies
  // ========================================
  {
    type: 'recommends',
    source: 'fumadocs_ai_search',
    sourceValue: 'enabled',
    target: 'fumadocs_search_provider',
    targetValue: 'orama',
    message: 'AI Search works best with Orama search provider',
  },
]

// Validate configuration against dependency rules
export function validateDependencies(config: Partial<RisoConfig>): DependencyWarning[] {
  const warnings: DependencyWarning[] = []

  for (const rule of DEPENDENCY_RULES) {
    const sourceValue = config[rule.source]
    const targetValue = config[rule.target]

    // Check if source condition matches
    const sourceMatches =
      rule.sourceValue === undefined || sourceValue === rule.sourceValue

    if (!sourceMatches) continue

    // Check if target condition is satisfied
    const targetSatisfied =
      rule.targetValue === undefined || targetValue === rule.targetValue

    if (!targetSatisfied) {
      warnings.push({
        type: rule.type === 'requires' ? 'error' : rule.type === 'conflicts' ? 'error' : 'info',
        field: rule.source,
        message: rule.message,
        relatedField: rule.target,
      })
    }
  }

  return warnings
}

// Check if a specific field is disabled due to dependencies
export function isFieldDisabled(
  field: keyof RisoConfig,
  config: RisoConfig
): { disabled: boolean; reason?: string } {
  // SaaS layer cascade
  if (field === 'saas_auth_module' && config.saas_infra_module !== 'enabled') {
    return {
      disabled: true,
      reason: 'Enable Infrastructure layer first',
    }
  }

  if (field === 'saas_billing_module' && config.saas_auth_module !== 'enabled') {
    return {
      disabled: true,
      reason: 'Enable Auth layer first',
    }
  }

  if (field === 'saas_app_module' && config.saas_infra_module !== 'enabled') {
    return {
      disabled: true,
      reason: 'Enable Infrastructure layer first',
    }
  }

  // Docs framework options - disabled if docs_module is disabled
  const fumadocsFields = [
    'fumadocs_search_provider',
    'fumadocs_llms_txt',
    'fumadocs_ai_search',
    'fumadocs_openapi',
    'fumadocs_theme',
    'fumadocs_blog',
    'fumadocs_mermaid',
    'fumadocs_math',
  ]

  const docusaurusFields = [
    'docusaurus_search_provider',
    'docusaurus_analytics',
    'docusaurus_theme',
    'docusaurus_blog',
    'docusaurus_mermaid',
    'docusaurus_math',
  ]

  if (fumadocsFields.includes(field) && config.docs_module !== 'enabled') {
    return {
      disabled: true,
      reason: 'Enable Documentation module first',
    }
  }

  if (
    fumadocsFields.includes(field) &&
    config.docs_framework !== 'fumadocs'
  ) {
    return {
      disabled: true,
      reason: 'Select Fumadocs as documentation framework',
    }
  }

  if (docusaurusFields.includes(field) && config.docs_module !== 'enabled') {
    return {
      disabled: true,
      reason: 'Enable Documentation module first',
    }
  }

  if (
    docusaurusFields.includes(field) &&
    config.docs_framework !== 'docusaurus'
  ) {
    return {
      disabled: true,
      reason: 'Select Docusaurus as documentation framework',
    }
  }

  // AI Tools options - disabled if ai_tools_module is disabled
  const aiToolsFields = [
    'ai_tools_mcp_thinking',
    'ai_tools_mcp_web',
    'ai_tools_mcp_documents',
    'ai_tools_mcp_utilities',
    'ai_tools_mcp_search',
  ]

  if (aiToolsFields.includes(field) && config.ai_tools_module !== 'enabled') {
    return {
      disabled: true,
      reason: 'Enable AI Tools module first',
    }
  }

  return { disabled: false }
}

// Get all fields that depend on a given field
export function getDependentFields(
  field: keyof RisoConfig
): (keyof RisoConfig)[] {
  const dependents: Set<keyof RisoConfig> = new Set()

  for (const rule of DEPENDENCY_RULES) {
    if (rule.target === field) {
      dependents.add(rule.source)
    }
  }

  return Array.from(dependents)
}

// Get all fields that a given field depends on
export function getRequiredFields(
  field: keyof RisoConfig
): (keyof RisoConfig)[] {
  const required: Set<keyof RisoConfig> = new Set()

  for (const rule of DEPENDENCY_RULES) {
    if (rule.source === field && rule.type === 'requires') {
      required.add(rule.target)
    }
  }

  return Array.from(required)
}

// Group dependencies by category for visualization
export const DEPENDENCY_GROUPS = {
  saas: {
    label: 'SaaS Architecture',
    description: 'Layered dependency: Infrastructure → Auth → Billing → App',
    fields: [
      'saas_infra_module',
      'saas_auth_module',
      'saas_billing_module',
      'saas_app_module',
    ],
  },
  docs: {
    label: 'Documentation',
    description: 'Framework-specific options depend on docs_module',
    fields: ['docs_module', 'docs_framework'],
  },
  ai: {
    label: 'AI Tools',
    description: 'MCP servers depend on ai_tools_module',
    fields: [
      'ai_tools_module',
      'ai_tools_mcp_thinking',
      'ai_tools_mcp_web',
      'ai_tools_mcp_documents',
    ],
  },
}
