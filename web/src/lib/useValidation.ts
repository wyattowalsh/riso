/**
 * useValidation Hook
 *
 * Custom hook for validation logic extraction.
 * Provides comprehensive validation including dependency checks,
 * validation rules, cost estimates, and enhanced warnings with quick fixes.
 */

import { useMemo } from 'react'
import { type RisoConfig } from './store'
import { validateDependencies } from './dependencies'
import { validateConfig, getCostEstimate, type ValidationResult } from './validation'

export interface Warning {
  id: string
  type: 'missing' | 'conflict' | 'recommendation'
  severity: 'error' | 'warning' | 'info'
  message: string
  details?: string
  fix?: {
    label: string
    action: () => void
  }
  relatedField?: keyof RisoConfig
}

export interface ValidationHookResult {
  warnings: Warning[]
  errors: Warning[]
  warningList: Warning[]
  infos: Warning[]
  costEstimate: ReturnType<typeof getCostEstimate>
  hasIssues: boolean
}

/**
 * Hook to validate configuration and generate warnings with quick-fix actions
 *
 * @param config - Current Riso configuration (partial allowed from store)
 * @param updateConfig - Function to update configuration
 * @param dismissedIds - Set of dismissed warning IDs
 * @returns Validation results with categorized warnings
 */
export function useValidation(
  config: Partial<RisoConfig>,
  updateConfig: (updates: Partial<RisoConfig>) => void,
  dismissedIds: Set<string> = new Set()
): ValidationHookResult {
  // Detect warnings from both dependencies and validation system
  const dependencyWarnings = useMemo(() => validateDependencies(config), [config])
  const validationResults = useMemo(() => validateConfig(config), [config])
  const costEstimate = useMemo(() => getCostEstimate(config), [config])

  // Enhanced warnings with quick-fix actions
  const enhancedWarnings = useMemo(() => {
    const warnings: Warning[] = []

    // Convert dependency warnings to enhanced warnings
    dependencyWarnings.forEach((dw, idx) => {
      warnings.push({
        id: `dep-${idx}`,
        type: dw.type === 'error' ? 'missing' : 'recommendation',
        severity: dw.type,
        message: dw.message,
        relatedField: dw.relatedField,
      })
    })

    // Convert validation results to enhanced warnings
    validationResults.forEach((vr: ValidationResult) => {
      warnings.push({
        id: vr.id,
        type:
          vr.severity === 'error'
            ? 'missing'
            : vr.severity === 'warning'
              ? 'conflict'
              : 'recommendation',
        severity: vr.severity,
        message: vr.message,
        details: vr.details,
        fix: vr.quickFix
          ? {
              label: vr.quickFix.label,
              action: () => {
                const updates = vr.quickFix!.apply(config)
                updateConfig(updates)
              },
            }
          : undefined,
        relatedField: vr.affectedFields[0],
      })
    })

    // Add custom warnings with quick-fix actions

    // SaaS Auth without provider
    if (config.saas_auth_module === 'enabled' && !config.saas_auth_provider) {
      warnings.push({
        id: 'saas-no-auth-provider',
        type: 'missing',
        severity: 'warning',
        message: 'Auth module enabled but no provider selected',
        details: 'Select an authentication provider like Clerk or Auth.js for production use',
        fix: {
          label: 'Use Clerk',
          action: () => updateConfig({ saas_auth_provider: 'clerk' }),
        },
        relatedField: 'saas_auth_provider',
      })
    }

    // SaaS Billing without provider
    if (config.saas_billing_module === 'enabled' && !config.saas_billing_provider) {
      warnings.push({
        id: 'saas-no-billing-provider',
        type: 'missing',
        severity: 'warning',
        message: 'Billing module enabled but no provider selected',
        details: 'Select a payment provider like Stripe for production use',
        fix: {
          label: 'Use Stripe',
          action: () => updateConfig({ saas_billing_provider: 'stripe' }),
        },
        relatedField: 'saas_billing_provider',
      })
    }

    // Rust MCP experimental warning
    if (config.mcp_module === 'enabled' && config.mcp_languages?.includes('rust')) {
      warnings.push({
        id: 'rust-mcp-experimental',
        type: 'conflict',
        severity: 'warning',
        message: 'Rust MCP server support is experimental',
        details: 'Consider using Python or TypeScript for production MCP servers with better ecosystem support',
        fix: {
          label: 'Use Python',
          action: () => updateConfig({ mcp_languages: ['python'] }),
        },
        relatedField: 'mcp_languages',
      })
    }

    // Quality profile recommendation for SaaS
    if (
      (config.saas_infra_module === 'enabled' ||
        config.saas_auth_module === 'enabled' ||
        config.saas_billing_module === 'enabled') &&
      config.quality_profile === 'standard'
    ) {
      warnings.push({
        id: 'saas-quality-strict',
        type: 'recommendation',
        severity: 'info',
        message: 'Consider strict quality profile for SaaS applications',
        details: 'Strict quality checks help catch issues early in production SaaS apps',
        fix: {
          label: 'Use Strict',
          action: () => updateConfig({ quality_profile: 'strict' }),
        },
        relatedField: 'quality_profile',
      })
    }

    // Docs without OpenAPI recommendation
    if (
      config.docs_module === 'enabled' &&
      config.api_module === 'enabled' &&
      config.docs_framework === 'fumadocs' &&
      config.fumadocs_openapi === 'disabled'
    ) {
      warnings.push({
        id: 'fumadocs-openapi-recommend',
        type: 'recommendation',
        severity: 'info',
        message: 'Enable OpenAPI docs for better API documentation',
        details: 'OpenAPI integration provides interactive API documentation',
        fix: {
          label: 'Enable OpenAPI',
          action: () => updateConfig({ fumadocs_openapi: 'enabled' }),
        },
        relatedField: 'fumadocs_openapi',
      })
    }

    // AI Search without Orama
    if (
      config.fumadocs_ai_search === 'enabled' &&
      config.fumadocs_search_provider !== 'orama' &&
      config.fumadocs_search_provider !== 'orama-cloud'
    ) {
      warnings.push({
        id: 'ai-search-orama',
        type: 'recommendation',
        severity: 'info',
        message: 'AI Search works best with Orama search provider',
        details: 'Orama provides vector search capabilities for better AI-powered search',
        fix: {
          label: 'Use Orama',
          action: () => updateConfig({ fumadocs_search_provider: 'orama' }),
        },
        relatedField: 'fumadocs_search_provider',
      })
    }

    // Monorepo without shared logic
    if (config.project_layout === 'monorepo' && config.shared_logic === 'disabled') {
      warnings.push({
        id: 'monorepo-shared-logic',
        type: 'recommendation',
        severity: 'info',
        message: 'Consider enabling shared logic for monorepo',
        details: 'Shared logic module helps organize common code across packages',
        fix: {
          label: 'Enable Shared Logic',
          action: () => updateConfig({ shared_logic: 'enabled' }),
        },
        relatedField: 'shared_logic',
      })
    }

    return warnings.filter((w) => !dismissedIds.has(w.id))
  }, [config, dependencyWarnings, validationResults, dismissedIds, updateConfig])

  const errors = enhancedWarnings.filter((w) => w.severity === 'error')
  const warningList = enhancedWarnings.filter((w) => w.severity === 'warning')
  const infos = enhancedWarnings.filter((w) => w.severity === 'info')

  return {
    warnings: enhancedWarnings,
    errors,
    warningList,
    infos,
    costEstimate,
    hasIssues: enhancedWarnings.length > 0,
  }
}
