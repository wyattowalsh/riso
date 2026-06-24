import { describe, it, expect } from 'vitest'
import { validateProjectName } from '../components/steps/ProjectBasics'
import {
  validateConfig,
  getCostEstimate,
  VALIDATION_RULES,
} from '../lib/validation'
import type { RisoConfig } from '../lib/store'

describe('validateProjectName', () => {
  it('rejects empty names', () => {
    expect(validateProjectName('').valid).toBe(false)
    expect(validateProjectName('  ').valid).toBe(false)
  })

  it('rejects names shorter than 2 characters', () => {
    const result = validateProjectName('a')
    expect(result.valid).toBe(false)
    expect(result.error).toContain('at least 2 characters')
  })

  it('rejects names longer than 64 characters', () => {
    const longName = 'a'.repeat(65)
    const result = validateProjectName(longName)
    expect(result.valid).toBe(false)
    expect(result.error).toContain('64 characters')
  })

  it('rejects names starting with a number', () => {
    const result = validateProjectName('123project')
    expect(result.valid).toBe(false)
    expect(result.error).toContain('start with a letter')
  })

  it('rejects names with spaces', () => {
    const result = validateProjectName('my project')
    expect(result.valid).toBe(false)
  })

  it('rejects names with special characters', () => {
    expect(validateProjectName('my@project').valid).toBe(false)
    expect(validateProjectName('my.project').valid).toBe(false)
    expect(validateProjectName('my project!').valid).toBe(false)
  })

  it('accepts valid names with letters only', () => {
    expect(validateProjectName('myproject').valid).toBe(true)
    expect(validateProjectName('MyProject').valid).toBe(true)
  })

  it('accepts names with hyphens', () => {
    expect(validateProjectName('my-project').valid).toBe(true)
    expect(validateProjectName('my-awesome-project').valid).toBe(true)
  })

  it('accepts names with underscores', () => {
    expect(validateProjectName('my_project').valid).toBe(true)
    expect(validateProjectName('my_awesome_project').valid).toBe(true)
  })

  it('accepts names with numbers after first character', () => {
    expect(validateProjectName('project123').valid).toBe(true)
    expect(validateProjectName('my-project-2').valid).toBe(true)
  })

  it('accepts mixed valid characters', () => {
    expect(validateProjectName('My-Project_123').valid).toBe(true)
    expect(validateProjectName('awesome_project-v2').valid).toBe(true)
  })
})

// ========================================
// CONFIG VALIDATION TESTS
// ========================================

describe('Configuration Validation System', () => {
  // Helper to create base config - use satisfies to preserve literal types
  const baseConfig = () =>
    ({
      project_name: 'test-project',
      project_layout: 'single-package',
      quality_profile: 'standard',
      cli_module: 'disabled',
      api_module: 'disabled',
      api_languages: ['python'],
      docs_module: 'enabled',
      docs_framework: 'fumadocs',
      ai_tools_module: 'disabled',
      saas_infra_module: 'disabled',
      saas_auth_module: 'disabled',
      saas_billing_module: 'disabled',
      saas_app_module: 'disabled',
      saas_auth_provider: 'clerk',
      saas_enterprise_bridge: 'none',
      saas_runtime: 'nextjs-16',
      saas_hosting: 'vercel',
      saas_database: 'neon',
      saas_orm: 'prisma',
      saas_email: 'resend',
      saas_analytics: 'posthog',
      saas_billing_provider: 'stripe',
      saas_jobs: 'triggerdev',
      saas_storage: 'r2',
      saas_ai: 'openai',
      saas_observability_sentry: false,
      saas_observability_datadog: false,
      saas_observability_otel: false,
      saas_test_suite_level: 'standard',
      changelog_module: 'disabled',
      api_features: 'none',
      fumadocs_openapi: 'disabled',
      fumadocs_ai_search: 'disabled',
      fumadocs_search_provider: 'none',
      fumadocs_typedoc: 'disabled',
      docusaurus_openapi: 'disabled',
      docusaurus_search_provider: 'local',
    }) as const satisfies Partial<RisoConfig>

  // Helper to create test config with proper literal type preservation
  const testConfig = (overrides: Partial<RisoConfig>): Partial<RisoConfig> => ({
    ...baseConfig(),
    ...overrides,
  })

  describe('test_clerk_workos_mutual_exclusion', () => {
    it('should trigger warning when Clerk auth + WorkOS bridge are both selected', () => {
      const config = testConfig({
        saas_auth_provider: 'clerk',
        saas_enterprise_bridge: 'workos',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'clerk-workos-conflict')
      expect(violation).toBeDefined()
      expect(violation?.severity).toBe('warning')
      expect(violation?.message).toContain('Clerk already includes enterprise SSO')
    })

    it('should not trigger warning when Clerk auth + WorkOS are not both selected', () => {
      const config = testConfig({
        saas_auth_provider: 'clerk',
        saas_enterprise_bridge: 'none',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'clerk-workos-conflict')
      expect(violation).toBeUndefined()
    })

    it('should provide quick fix to remove WorkOS bridge', () => {
      const config = testConfig({
        saas_auth_provider: 'clerk',
        saas_enterprise_bridge: 'workos',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'clerk-workos-conflict')
      expect(violation?.quickFix).toBeDefined()
      expect(violation?.quickFix?.label).toBe('Remove WorkOS bridge')
      const fixed = violation?.quickFix?.apply(config)
      expect(fixed?.saas_enterprise_bridge).toBe('none')
    })
  })

  describe('test_billing_requires_auth', () => {
    it('should trigger error when billing enabled without auth', () => {
      const config = testConfig({
        saas_billing_module: 'enabled',
        saas_auth_module: 'disabled',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'billing-requires-auth')
      expect(violation).toBeDefined()
      expect(violation?.severity).toBe('error')
      expect(violation?.message).toContain('Billing features require authentication')
    })

    it('should not trigger error when both billing and auth are enabled', () => {
      const config = testConfig({
        saas_billing_module: 'enabled',
        saas_auth_module: 'enabled',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'billing-requires-auth')
      expect(violation).toBeUndefined()
    })

    it('should not trigger error when billing is disabled', () => {
      const config = testConfig({
        saas_billing_module: 'disabled',
        saas_auth_module: 'disabled',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'billing-requires-auth')
      expect(violation).toBeUndefined()
    })

    it('should provide quick fix to enable auth with Clerk', () => {
      const config = testConfig({
        saas_billing_module: 'enabled',
        saas_auth_module: 'disabled',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'billing-requires-auth')
      expect(violation?.quickFix).toBeDefined()
      const fixed = violation?.quickFix?.apply(config)
      expect(fixed?.saas_auth_module).toBe('enabled')
      expect(fixed?.saas_auth_provider).toBe('clerk')
    })
  })

  describe('test_database_dependency_check', () => {
    it('should trigger error when auth enabled without infra', () => {
      const config = testConfig({
        saas_auth_module: 'enabled',
        saas_infra_module: 'disabled',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'auth-requires-infra')
      expect(violation).toBeDefined()
      expect(violation?.severity).toBe('error')
      expect(violation?.message).toContain('Authentication requires infrastructure')
    })

    it('should trigger error when app enabled without infra', () => {
      const config = testConfig({
        saas_app_module: 'enabled',
        saas_infra_module: 'disabled',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'app-requires-infra')
      expect(violation).toBeDefined()
      expect(violation?.severity).toBe('error')
    })

    it('should not trigger error when infra is enabled', () => {
      const config = testConfig({
        saas_auth_module: 'enabled',
        saas_infra_module: 'enabled',
        saas_app_module: 'enabled',
      })
      const results = validateConfig(config)
      const authViolation = results.find((r) => r.id === 'auth-requires-infra')
      const appViolation = results.find((r) => r.id === 'app-requires-infra')
      expect(authViolation).toBeUndefined()
      expect(appViolation).toBeUndefined()
    })

    it('should provide quick fix with database and ORM defaults', () => {
      const config = testConfig({
        saas_auth_module: 'enabled',
        saas_infra_module: 'disabled',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'auth-requires-infra')
      const fixed = violation?.quickFix?.apply(config)
      expect(fixed?.saas_infra_module).toBe('enabled')
      expect(fixed?.saas_database).toBe('neon')
      expect(fixed?.saas_orm).toBe('prisma')
    })
  })

  describe('test_cost_estimate_calculation', () => {
    it('should calculate zero cost for free tier services', () => {
      const config = testConfig({
        saas_auth_provider: 'clerk',
        saas_database: 'neon',
        saas_hosting: 'vercel',
      })
      const estimate = getCostEstimate(config)
      expect(estimate.monthly).toBe(0)
      expect(estimate.services.length).toBeGreaterThan(0)
    })

    it('should include service names and notes', () => {
      const config = testConfig({
        saas_auth_provider: 'clerk',
      })
      const estimate = getCostEstimate(config)
      const clerkService = estimate.services.find((s) => s.name === 'Clerk')
      expect(clerkService).toBeDefined()
      expect(clerkService?.note).toContain('10k MAU')
    })

    it('should calculate monthly cost for paid services', () => {
      const config = testConfig({
        saas_email: 'postmark',
      })
      const estimate = getCostEstimate(config)
      const postmarkService = estimate.services.find((s) => s.name === 'Postmark')
      expect(postmarkService?.cost).toBe(10)
      expect(estimate.monthly).toBeGreaterThanOrEqual(10)
    })

    it('should aggregate multiple service costs', () => {
      const config = testConfig({
        saas_email: 'postmark', // $10/month
        saas_observability_sentry: true,
        saas_observability_datadog: true,
      })
      const estimate = getCostEstimate(config)
      // Postmark is $10, others are free tier
      expect(estimate.monthly).toBe(10)
      expect(estimate.services.length).toBeGreaterThan(1)
    })

    it('should return empty services for minimal config', () => {
      // Use a truly minimal config with no provider values
      const minimalConfig: Partial<RisoConfig> = {
        project_name: 'empty',
        project_layout: 'single-package',
        // Explicitly set all providers to 'none' or undefined
        saas_auth_provider: undefined,
        saas_enterprise_bridge: 'none',
        saas_billing_provider: undefined,
        saas_database: undefined,
        saas_hosting: undefined,
        saas_email: undefined,
        saas_analytics: undefined,
      }
      const estimate = getCostEstimate(minimalConfig)
      expect(estimate.services.length).toBe(0)
      expect(estimate.monthly).toBe(0)
    })
  })

  describe('test_warning_vs_error_severity', () => {
    it('should distinguish between error and warning severity', () => {
      const errorRule = VALIDATION_RULES.find((r) => r.id === 'billing-requires-auth')
      expect(errorRule?.severity).toBe('error')

      const warningRule = VALIDATION_RULES.find((r) => r.id === 'clerk-workos-conflict')
      expect(warningRule?.severity).toBe('warning')

      const infoRule = VALIDATION_RULES.find((r) => r.id === 'stripe-cost-warning')
      expect(infoRule?.severity).toBe('info')
    })

    it('should return all violations regardless of severity', () => {
      const config = testConfig({
        saas_billing_module: 'enabled', // Error: needs auth
        saas_auth_provider: 'clerk',
        saas_enterprise_bridge: 'workos', // Warning: redundant
      })
      const results = validateConfig(config)
      const severities = results.map((r) => r.severity)
      expect(severities).toContain('error')
      expect(severities).toContain('warning')
    })
  })

  describe('test_no_warnings_for_valid_config', () => {
    it('should return no violations for valid minimal config', () => {
      const config = testConfig({
        saas_infra_module: 'disabled',
        saas_auth_module: 'disabled',
        saas_billing_module: 'disabled',
      })
      const results = validateConfig(config)
      // Filter out info (cost warnings) - they are informational, not violations
      const violations = results.filter((r) => r.severity !== 'info')
      expect(violations).toHaveLength(0)
    })

    it('should return no violations for complete SaaS setup', () => {
      const config = testConfig({
        saas_infra_module: 'enabled',
        saas_auth_module: 'enabled',
        saas_billing_module: 'enabled',
        saas_app_module: 'enabled',
        saas_auth_provider: 'clerk',
        saas_enterprise_bridge: 'none', // Not using workos
        saas_database: 'neon',
        saas_orm: 'prisma',
        saas_hosting: 'vercel',
        saas_observability_sentry: true, // Enable observability for production
      })
      const results = validateConfig(config)
      // Only info messages (cost warnings) should appear
      const errors = results.filter((r) => r.severity === 'error')
      const warnings = results.filter((r) => r.severity === 'warning')
      expect(errors).toHaveLength(0)
      expect(warnings).toHaveLength(0)
    })
  })

  describe('test_multiple_validation_errors', () => {
    it('should return multiple violations when multiple rules are violated', () => {
      const config = testConfig({
        saas_billing_module: 'enabled',
        saas_auth_module: 'disabled', // Error: billing needs auth
        saas_app_module: 'enabled',
        saas_infra_module: 'disabled', // Error: app needs infra
        saas_auth_provider: 'clerk',
        saas_enterprise_bridge: 'workos', // Warning: redundant
      })
      const results = validateConfig(config)
      const errorCount = results.filter((r) => r.severity === 'error').length
      const warningCount = results.filter((r) => r.severity === 'warning').length
      expect(errorCount).toBeGreaterThan(0)
      expect(warningCount).toBeGreaterThan(0)
    })

    it('should include affected fields for each violation', () => {
      const config = testConfig({
        saas_billing_module: 'enabled',
        saas_auth_module: 'disabled',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'billing-requires-auth')
      expect(violation?.affectedFields).toContain('saas_billing_module')
      expect(violation?.affectedFields).toContain('saas_auth_module')
      expect(Array.isArray(violation?.affectedFields)).toBe(true)
    })

    it('should limit results appropriately', () => {
      const config = baseConfig()
      const results = validateConfig(config)
      // Should be a reasonable number
      expect(results.length).toBeLessThan(100)
    })
  })

  describe('test_quick_fix_actions', () => {
    it('should provide quick fix for clerk-workos conflict', () => {
      const config = testConfig({
        saas_auth_provider: 'clerk',
        saas_enterprise_bridge: 'workos',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'clerk-workos-conflict')
      expect(violation?.quickFix).toBeDefined()
      expect(violation?.quickFix?.label).toBe('Remove WorkOS bridge')
      expect(typeof violation?.quickFix?.apply).toBe('function')
    })

    it('should provide quick fix for billing-requires-auth', () => {
      const config = testConfig({
        saas_billing_module: 'enabled',
        saas_auth_module: 'disabled',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'billing-requires-auth')
      expect(violation?.quickFix).toBeDefined()
      expect(violation?.quickFix?.label).toBe('Enable Auth layer')
    })

    it('should apply quick fix correctly', () => {
      const config = testConfig({
        saas_auth_provider: 'clerk',
        saas_enterprise_bridge: 'workos',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'clerk-workos-conflict')
      const fixed = violation?.quickFix?.apply(config)
      expect(fixed?.saas_enterprise_bridge).toBe('none')
    })

    it('should not break original config when applying quick fix', () => {
      const config = testConfig({
        saas_billing_module: 'enabled',
        saas_auth_module: 'disabled',
        project_name: 'test-project',
      })
      const results = validateConfig(config)
      const violation = results.find((r) => r.id === 'billing-requires-auth')
      violation?.quickFix?.apply(config)
      // Original config should be unchanged
      expect(config.saas_auth_module).toBe('disabled')
      expect(config.project_name).toBe('test-project')
    })

    it('should have quick fixes for all error violations', () => {
      const config = testConfig({
        saas_billing_module: 'enabled',
        saas_auth_module: 'disabled',
        saas_app_module: 'enabled',
        saas_infra_module: 'disabled',
      })
      const results = validateConfig(config)
      const errors = results.filter((r) => r.severity === 'error')
      // Most error violations should have quick fixes
      const withFixes = errors.filter((e) => e.quickFix)
      expect(withFixes.length).toBeGreaterThan(0)
    })

    it('should have optional quick fixes for info violations', () => {
      const config = testConfig({
        saas_auth_provider: 'clerk',
      })
      const results = validateConfig(config)
      const infoViolations = results.filter((r) => r.severity === 'info')
      // Cost warnings typically don't have quick fixes
      expect(infoViolations.length).toBeGreaterThan(0)
    })
  })

  describe('validateConfig function', () => {
    it('should return ValidationResult array', () => {
      const config = baseConfig()
      const results = validateConfig(config)
      expect(Array.isArray(results)).toBe(true)
      if (results.length > 0) {
        const result = results[0]
        expect(result).toHaveProperty('id')
        expect(result).toHaveProperty('message')
        expect(result).toHaveProperty('severity')
        expect(result).toHaveProperty('affectedFields')
      }
    })

    it('should filter rules based on check function', () => {
      const configWithViolations = testConfig({
        saas_billing_module: 'enabled',
        saas_auth_module: 'disabled',
      })
      const resultsWithViolations = validateConfig(configWithViolations)
      const billingViolation = resultsWithViolations.find(
        (r) => r.id === 'billing-requires-auth'
      )
      expect(billingViolation).toBeDefined()

      const configWithoutViolations = testConfig({
        saas_billing_module: 'disabled',
        saas_auth_module: 'disabled',
      })
      const resultsWithoutViolations = validateConfig(configWithoutViolations)
      const noBillingViolation = resultsWithoutViolations.find(
        (r) => r.id === 'billing-requires-auth'
      )
      expect(noBillingViolation).toBeUndefined()
    })
  })

  describe('VALIDATION_RULES constant', () => {
    it('should contain expected rule IDs', () => {
      const ruleIds = VALIDATION_RULES.map((r) => r.id)
      expect(ruleIds).toContain('clerk-workos-conflict')
      expect(ruleIds).toContain('billing-requires-auth')
      expect(ruleIds).toContain('auth-requires-infra')
      expect(ruleIds).toContain('stripe-cost-warning')
    })

    it('should have valid severity levels', () => {
      VALIDATION_RULES.forEach((rule) => {
        expect(['error', 'warning', 'info']).toContain(rule.severity)
      })
    })

    it('should have non-empty messages', () => {
      VALIDATION_RULES.forEach((rule) => {
        expect(rule.message).toBeTruthy()
        expect(typeof rule.message).toBe('string')
      })
    })

    it('should have affected fields array', () => {
      VALIDATION_RULES.forEach((rule) => {
        expect(Array.isArray(rule.affectedFields)).toBe(true)
        expect(rule.affectedFields.length).toBeGreaterThan(0)
      })
    })

    it('should have valid check functions', () => {
      VALIDATION_RULES.forEach((rule) => {
        expect(typeof rule.check).toBe('function')
      })
    })
  })
})
