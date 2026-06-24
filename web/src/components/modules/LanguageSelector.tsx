import { cn } from '../../lib/utils'

/**
 * Language option configuration
 */
export interface LanguageOption {
  /** Unique value identifier for the language */
  value: string
  /** Display label for the language */
  label: string
  /** Description text (e.g., framework or library name) */
  description: string
  /** Optional icon string or emoji */
  icon?: string
}

/**
 * Props for the LanguageSelector component
 */
export interface LanguageSelectorProps {
  /** Array of language options to display */
  options: LanguageOption[]
  /** Currently selected language values */
  values: string[]
  /** Callback when the selection changes */
  onChange: (values: string[]) => void
  /** Whether the selector is disabled */
  disabled?: boolean
  /** Optional label to display above the selector */
  label?: string
  /** Optional helper text to display with the label */
  helperText?: string
}

/**
 * A multi-select language picker component with checkbox grid layout.
 * Ensures at least one language is always selected.
 *
 * @example
 * ```tsx
 * <LanguageSelector
 *   label="Implementation Languages"
 *   helperText="(select multiple)"
 *   options={CLI_LANGUAGES}
 *   values={config.cli_languages || ['python']}
 *   onChange={(v) => updateConfig({ cli_languages: v })}
 * />
 * ```
 */
export function LanguageSelector({
  options,
  values,
  onChange,
  disabled = false,
  label,
  helperText
}: LanguageSelectorProps) {
  const toggleLanguage = (lang: string) => {
    if (values.includes(lang)) {
      // Don't allow deselecting if it's the only one selected
      if (values.length > 1) {
        onChange(values.filter((v) => v !== lang))
      }
    } else {
      onChange([...values, lang])
    }
  }

  return (
    <div>
      {label && (
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
          {label}{' '}
          {helperText && (
            <span className="text-gray-400 font-normal">{helperText}</span>
          )}
        </label>
      )}
      <div
        className={cn(
          'grid grid-cols-2 sm:grid-cols-4 gap-2',
          disabled && 'opacity-50'
        )}
      >
        {options.map((option) => {
          const isSelected = values.includes(option.value)
          return (
            <button
              key={option.value}
              type="button"
              disabled={disabled}
              onClick={() => toggleLanguage(option.value)}
              className={cn(
                'p-3 rounded-lg text-left transition-all border relative',
                isSelected
                  ? 'border-riso-federal-blue dark:border-riso-teal bg-riso-federal-blue/5 dark:bg-riso-teal/10'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              )}
              aria-pressed={isSelected}
            >
              {/* Checkbox indicator */}
              <div
                className={cn(
                  'absolute top-2 right-2 w-4 h-4 rounded border flex items-center justify-center',
                  isSelected
                    ? 'bg-riso-federal-blue dark:bg-riso-teal border-riso-federal-blue dark:border-riso-teal'
                    : 'border-gray-300 dark:border-gray-600'
                )}
              >
                {isSelected && (
                  <svg
                    className="w-3 h-3 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </div>
              <div className="font-medium text-sm text-gray-900 dark:text-white">
                {option.label}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {option.description}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
