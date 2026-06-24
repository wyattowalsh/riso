import { cn } from '../../lib/utils'

/**
 * Toggle option configuration
 */
export interface ToggleOption {
  /** Unique value for this option */
  value: string
  /** Display label */
  label: string
  /** Optional description shown as tooltip */
  description?: string
}

/**
 * Props for the FeatureToggleGroup component
 */
export interface FeatureToggleGroupProps {
  /** Label displayed above the toggle buttons */
  label: string
  /** Array of toggle options to display */
  options: ToggleOption[]
  /** Currently selected value */
  value: string
  /** Callback when a different option is selected */
  onChange: (value: string) => void
  /** Whether the toggle group is disabled */
  disabled?: boolean
}

/**
 * A group of toggle buttons for selecting between mutually exclusive options.
 * Displays as a horizontal row of pill-shaped buttons.
 *
 * @example
 * ```tsx
 * <FeatureToggleGroup
 *   label="API Features (Python only)"
 *   options={API_FEATURES}
 *   value={config.api_features || 'none'}
 *   onChange={(v) => updateConfig({ api_features: v })}
 * />
 * ```
 */
export function FeatureToggleGroup({
  label,
  options,
  value,
  onChange,
  disabled = false
}: FeatureToggleGroupProps) {
  return (
    <div className={cn(disabled && 'opacity-50')}>
      {label && (
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {label}
        </h4>
      )}
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            disabled={disabled}
            aria-pressed={value === option.value}
            onClick={() => onChange(option.value)}
            className={cn(
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
              value === option.value
                ? 'bg-riso-federal-blue dark:bg-riso-teal text-white shadow-sm'
                : 'bg-white/80 dark:bg-gray-800/80 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            )}
            title={option.description}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  )
}
