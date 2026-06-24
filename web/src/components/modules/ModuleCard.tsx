import { cn } from '../../lib/utils'

/**
 * Accent color variants for the module card
 */
export type AccentColor = 'blue' | 'green' | 'purple' | 'orange' | 'teal'

/**
 * Props for the ModuleCard component
 */
export interface ModuleCardProps {
  /** Title of the module */
  title: string
  /** Description text shown below the title */
  description: string
  /** Icon component to display (from lucide-react) */
  icon: React.ElementType
  /** Whether the module is currently enabled */
  enabled: boolean
  /** Callback when the toggle switch is clicked */
  onToggle: (enabled: boolean) => void
  /** Optional child content shown when the module is enabled */
  children?: React.ReactNode
  /** Accent color for enabled state styling */
  accentColor?: AccentColor
  /** Optional badge text (e.g., "recommended") */
  badge?: string
}

/**
 * A reusable card component for module configuration.
 * Displays a module with an icon, title, description, and toggle switch.
 * When enabled, can show additional configuration options as children.
 *
 * @example
 * ```tsx
 * <ModuleCard
 *   title="CLI Application"
 *   description="Command-line interface with argument parsing"
 *   icon={Terminal}
 *   enabled={config.cli_module === 'enabled'}
 *   onToggle={(enabled) => updateConfig({ cli_module: enabled ? 'enabled' : 'disabled' })}
 *   accentColor="blue"
 * >
 *   <LanguageSelector ... />
 * </ModuleCard>
 * ```
 */
export function ModuleCard({
  title,
  description,
  icon: Icon,
  enabled,
  onToggle,
  children,
  accentColor = 'blue',
  badge
}: ModuleCardProps) {
  const accentClasses: Record<AccentColor, string> = {
    blue: 'border-riso-federal-blue/30 bg-riso-federal-blue/5',
    green: 'border-riso-green/30 bg-riso-green/5',
    purple: 'border-riso-grape/30 bg-riso-grape/5',
    orange: 'border-riso-orange/30 bg-riso-orange/5',
    teal: 'border-riso-teal/30 bg-riso-teal/5',
  }

  const iconClasses: Record<AccentColor, string> = {
    blue: 'text-riso-federal-blue dark:text-riso-cornflower',
    green: 'text-riso-green dark:text-riso-mint',
    purple: 'text-riso-grape dark:text-riso-fluorescent-pink',
    orange: 'text-riso-orange dark:text-riso-apricot',
    teal: 'text-riso-teal dark:text-riso-mint',
  }

  return (
    <div
      className={cn(
        'rounded-xl border-2 p-4 transition-all',
        enabled
          ? accentClasses[accentColor]
          : 'border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/30'
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1">
          <div
            className={cn(
              'p-2 rounded-lg',
              enabled
                ? `${accentClasses[accentColor]}`
                : 'bg-gray-100 dark:bg-gray-700'
            )}
          >
            <Icon
              className={cn(
                'h-5 w-5',
                enabled ? iconClasses[accentColor] : 'text-gray-400'
              )}
            />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-900 dark:text-white">
                {title}
              </h3>
              {badge && (
                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-riso-federal-blue/10 dark:bg-riso-teal/10 text-riso-federal-blue dark:text-riso-teal">
                  {badge}
                </span>
              )}
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
              {description}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => onToggle(!enabled)}
          className={cn(
            'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out',
            enabled
              ? 'bg-riso-federal-blue dark:bg-riso-teal'
              : 'bg-gray-200 dark:bg-gray-600'
          )}
          aria-label={`Toggle ${title}`}
        >
          <span
            className={cn(
              'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
              enabled ? 'translate-x-5' : 'translate-x-0'
            )}
          />
        </button>
      </div>

      {enabled && children && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 space-y-4">
          {children}
        </div>
      )}
    </div>
  )
}
