import { useRisoStore } from '../../lib/store'
import { buildChoiceOptions, getPromptDefault, getPromptHelpSummary } from '../../lib/matrixData'
import { cn } from '../../lib/utils'

// Validation for project name: alphanumeric, hyphens, underscores, must start with letter
const PROJECT_NAME_REGEX = /^[a-zA-Z][a-zA-Z0-9_-]*$/

export function validateProjectName(name: string): { valid: boolean; error?: string } {
  if (!name || name.trim() === '') {
    return { valid: false, error: 'Project name is required' }
  }
  if (name.length < 2) {
    return { valid: false, error: 'Project name must be at least 2 characters' }
  }
  if (name.length > 64) {
    return { valid: false, error: 'Project name must be 64 characters or less' }
  }
  if (!PROJECT_NAME_REGEX.test(name)) {
    return { valid: false, error: 'Must start with a letter, contain only letters, numbers, hyphens, and underscores' }
  }
  return { valid: true }
}

export function ProjectBasics() {
  const { config, updateConfig } = useRisoStore()

  const projectLayoutOptions = buildChoiceOptions({
    key: 'project_layout',
    fallbackChoices: ['single-package', 'monorepo'],
    labels: {
      'single-package': 'Single Package',
      monorepo: 'Monorepo',
    },
  })
  const qualityOptions = buildChoiceOptions({
    key: 'quality_profile',
    fallbackChoices: ['standard', 'strict'],
    labels: {
      standard: 'Standard (recommended)',
      strict: 'Strict (90%+ coverage required)',
    },
  })
  const ciOptions = buildChoiceOptions({
    key: 'ci_platform',
    fallbackChoices: ['github-actions', 'none'],
    labels: {
      'github-actions': 'GitHub Actions',
      none: 'None',
    },
  })
  const defaultLayout = getPromptDefault<'single-package' | 'monorepo'>(
    'project_layout',
    'single-package'
  )
  const defaultQuality = getPromptDefault<'standard' | 'strict'>(
    'quality_profile',
    'standard'
  )
  const defaultCi = getPromptDefault<'github-actions' | 'none'>(
    'ci_platform',
    'github-actions'
  )

  const validation = validateProjectName(config.project_name || '')

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-display font-semibold text-gray-900 dark:text-white">Project Basics</h2>
        <p className="mt-1 text-gray-500 dark:text-gray-400">Set the identity and layout for your template.</p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        {/* Project Name */}
        <div className="sm:col-span-2">
          <label htmlFor="projectName" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Project Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="projectName"
            value={config.project_name || ''}
            onChange={(e) => updateConfig({ project_name: e.target.value })}
            placeholder="my-awesome-project"
            className={cn(
              "mt-1 block w-full rounded-lg border bg-white dark:bg-gray-700 px-4 py-2.5 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2",
              validation.valid || !config.project_name
                ? "border-gray-300 dark:border-gray-600 focus:border-riso-500 focus:ring-riso-500"
                : "border-red-500 focus:border-red-500 focus:ring-red-500"
            )}
          />
          {validation.error && config.project_name ? (
            <p className="mt-1 text-xs text-red-500">{validation.error}</p>
          ) : (
            <p className="mt-1 text-xs text-gray-500">Letters, numbers, hyphens, and underscores only</p>
          )}
        </div>

        {/* Project Layout */}
        <div>
          <label htmlFor="projectLayout" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Repository Layout
          </label>
          <select
            id="projectLayout"
            value={config.project_layout || defaultLayout}
            onChange={(e) => updateConfig({ project_layout: e.target.value as 'single-package' | 'monorepo' })}
            className="mt-1 block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2.5 text-gray-900 dark:text-white focus:border-riso-500 focus:ring-riso-500"
          >
            {projectLayoutOptions.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
          {getPromptHelpSummary('project_layout') && (
            <p className="mt-1 text-xs text-gray-500">{getPromptHelpSummary('project_layout')}</p>
          )}
        </div>

        {/* Quality Profile */}
        <div>
          <label htmlFor="qualityProfile" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Quality Profile
          </label>
          <select
            id="qualityProfile"
            value={config.quality_profile || defaultQuality}
            onChange={(e) => updateConfig({ quality_profile: e.target.value as 'standard' | 'strict' })}
            className="mt-1 block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2.5 text-gray-900 dark:text-white focus:border-riso-500 focus:ring-riso-500"
          >
            {qualityOptions.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
          {getPromptHelpSummary('quality_profile') && (
            <p className="mt-1 text-xs text-gray-500">{getPromptHelpSummary('quality_profile')}</p>
          )}
        </div>

        {/* CI Platform */}
        <div>
          <label htmlFor="ciPlatform" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            CI/CD Platform
          </label>
          <select
            id="ciPlatform"
            value={config.ci_platform || defaultCi}
            onChange={(e) => updateConfig({ ci_platform: e.target.value as 'github-actions' | 'none' })}
            className="mt-1 block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2.5 text-gray-900 dark:text-white focus:border-riso-500 focus:ring-riso-500"
          >
            {ciOptions.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
          {getPromptHelpSummary('ci_platform') && (
            <p className="mt-1 text-xs text-gray-500">{getPromptHelpSummary('ci_platform')}</p>
          )}
        </div>
      </div>
    </div>
  )
}
