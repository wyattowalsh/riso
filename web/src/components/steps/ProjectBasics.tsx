import { useRisoStore } from '../../lib/store'
import { getPromptDefault, getPromptHelpSummary } from '../../lib/matrixData'
import { cn } from '../../lib/utils'
import { Folder, GitBranch, Shield, Workflow, Check, Sparkles } from 'lucide-react'

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

interface OptionCardProps {
  value: string
  label: string
  description: string
  icon: React.ElementType
  selected: boolean
  onClick: () => void
}

function OptionCard({ label, description, icon: Icon, selected, onClick }: OptionCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'group relative p-4 rounded-xl border-2 text-left transition-all duration-300 overflow-hidden',
        selected
          ? 'border-riso-federal-blue dark:border-riso-teal bg-gradient-to-br from-riso-federal-blue/5 to-riso-teal/5 dark:from-riso-teal/10 dark:to-riso-federal-blue/10 shadow-lg shadow-riso-federal-blue/10 dark:shadow-riso-teal/10 scale-[1.02]'
          : 'border-gray-200 dark:border-gray-700 hover:border-riso-federal-blue/50 dark:hover:border-riso-teal/50 hover:shadow-md hover:-translate-y-0.5 bg-white/50 dark:bg-gray-800/50'
      )}
    >
      {/* Selection indicator */}
      {selected && (
        <span className="absolute top-3 right-3 flex h-5 w-5 items-center justify-center rounded-full bg-riso-federal-blue dark:bg-riso-teal text-white animate-bounce-in">
          <Check className="h-3 w-3" />
        </span>
      )}

      {/* Hover shine effect */}
      <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/10 to-transparent pointer-events-none" />

      <div className="flex items-start gap-3">
        <div
          className={cn(
            'relative p-2.5 rounded-xl transition-all duration-300',
            selected
              ? 'bg-gradient-to-br from-riso-federal-blue/20 to-riso-teal/20 dark:from-riso-teal/30 dark:to-riso-federal-blue/30'
              : 'bg-gray-100 dark:bg-gray-700 group-hover:bg-riso-federal-blue/10 dark:group-hover:bg-riso-teal/20'
          )}
        >
          <Icon
            className={cn(
              'h-5 w-5 transition-all duration-300',
              selected
                ? 'text-riso-federal-blue dark:text-riso-teal scale-110'
                : 'text-gray-400 group-hover:text-riso-federal-blue dark:group-hover:text-riso-teal group-hover:scale-110'
            )}
          />
          {selected && (
            <span className="absolute -top-1 -right-1">
              <Sparkles className="h-3 w-3 text-riso-sunflower animate-pulse" />
            </span>
          )}
        </div>
        <div className="flex-1">
          <div className={cn(
            'font-semibold transition-colors duration-300',
            selected
              ? 'text-riso-federal-blue dark:text-riso-teal'
              : 'text-gray-900 dark:text-white group-hover:text-riso-federal-blue dark:group-hover:text-riso-teal'
          )}>
            {label}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-1 leading-relaxed">
            {description}
          </div>
        </div>
      </div>
    </button>
  )
}

export function ProjectBasics() {
  const { config, updateConfig } = useRisoStore()

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
    <div className="space-y-8">
      {/* Header Section */}
      <div>
        <h2 className="display-md text-gray-900 dark:text-white">Project Basics</h2>
        <p className="mt-2 text-gray-500 dark:text-gray-400">
          Set the foundation for your project. You'll choose languages per-component in the next step.
        </p>
      </div>

      {/* Project Name */}
      <div>
        <label htmlFor="projectName" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Project Name <span className="text-riso-bright-red">*</span>
        </label>
        <input
          type="text"
          id="projectName"
          value={config.project_name || ''}
          onChange={(e) => updateConfig({ project_name: e.target.value })}
          placeholder="my-awesome-project"
          className={cn(
            'input-riso transition-all duration-200 text-lg',
            validation.valid || !config.project_name
              ? 'border-gray-300 dark:border-gray-600'
              : 'border-riso-bright-red dark:border-riso-bright-red'
          )}
        />
        <div className="mt-2">
          {validation.error && config.project_name ? (
            <p className="text-sm text-riso-bright-red font-medium">{validation.error}</p>
          ) : (
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Letters, numbers, hyphens, and underscores only
            </p>
          )}
        </div>
      </div>

      {/* Repository Layout */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Repository Layout
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          <OptionCard
            value="single-package"
            label="Single Package"
            description="One package, simpler structure for focused projects"
            icon={Folder}
            selected={(config.project_layout || defaultLayout) === 'single-package'}
            onClick={() => updateConfig({ project_layout: 'single-package' })}
          />
          <OptionCard
            value="monorepo"
            label="Monorepo"
            description="Multiple packages sharing tooling, ideal for polyglot stacks"
            icon={GitBranch}
            selected={(config.project_layout || defaultLayout) === 'monorepo'}
            onClick={() => updateConfig({ project_layout: 'monorepo' })}
          />
        </div>
        {getPromptHelpSummary('project_layout') && (
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            {getPromptHelpSummary('project_layout')}
          </p>
        )}
      </div>

      {/* Quality Profile */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Quality Profile
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          <OptionCard
            value="standard"
            label="Standard"
            description="Balanced linting, 80% coverage target, recommended for most projects"
            icon={Shield}
            selected={(config.quality_profile || defaultQuality) === 'standard'}
            onClick={() => updateConfig({ quality_profile: 'standard' })}
          />
          <OptionCard
            value="strict"
            label="Strict"
            description="Aggressive linting, 90%+ coverage, mutation testing"
            icon={Shield}
            selected={(config.quality_profile || defaultQuality) === 'strict'}
            onClick={() => updateConfig({ quality_profile: 'strict' })}
          />
        </div>
        {getPromptHelpSummary('quality_profile') && (
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            {getPromptHelpSummary('quality_profile')}
          </p>
        )}
      </div>

      {/* CI Platform */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          CI/CD Platform
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          <OptionCard
            value="github-actions"
            label="GitHub Actions"
            description="Pre-configured workflows for testing, linting, and releases"
            icon={Workflow}
            selected={(config.ci_platform || defaultCi) === 'github-actions'}
            onClick={() => updateConfig({ ci_platform: 'github-actions' })}
          />
          <OptionCard
            value="none"
            label="None"
            description="Skip CI configuration, add manually later"
            icon={Workflow}
            selected={(config.ci_platform || defaultCi) === 'none'}
            onClick={() => updateConfig({ ci_platform: 'none' })}
          />
        </div>
        {getPromptHelpSummary('ci_platform') && (
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            {getPromptHelpSummary('ci_platform')}
          </p>
        )}
      </div>
    </div>
  )
}
