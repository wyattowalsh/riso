import { cn } from '../../lib/utils'

export type SwitchAccent = 'blue' | 'orange' | 'teal'

export interface SwitchProps {
  checked: boolean
  onCheckedChange: (checked: boolean) => void
  labelledBy?: string
  label?: string
  disabled?: boolean
  accent?: SwitchAccent
}

const ACCENT_ON: Record<SwitchAccent, string> = {
  blue: 'bg-riso-federal-blue dark:bg-riso-teal',
  orange: 'bg-riso-orange',
  teal: 'bg-riso-teal',
}

/**
 * Named switch with a visible On/Off label (not color-only).
 */
export function Switch({
  checked,
  onCheckedChange,
  labelledBy,
  label,
  disabled = false,
  accent = 'blue',
}: SwitchProps) {
  return (
    <span className="inline-flex items-center gap-2">
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-labelledby={labelledBy}
        aria-label={labelledBy ? undefined : label}
        disabled={disabled}
        onClick={() => onCheckedChange(!checked)}
        className={cn(
          'relative inline-flex h-6 w-11 flex-shrink-0 rounded-full border-2 border-transparent transition-colors duration-200',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-riso-federal-blue focus-visible:ring-offset-2 dark:focus-visible:ring-riso-cornflower',
          disabled
            ? 'cursor-not-allowed bg-gray-200 dark:bg-gray-600'
            : checked
              ? cn('cursor-pointer', ACCENT_ON[accent])
              : 'cursor-pointer bg-gray-200 dark:bg-gray-600',
        )}
      >
        <span
          className={cn(
            'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200',
            checked ? 'translate-x-5' : 'translate-x-0',
          )}
        />
      </button>
      <span
        className="min-w-[1.75rem] text-xs font-semibold text-gray-700 dark:text-gray-300"
        aria-hidden="true"
      >
        {checked ? 'On' : 'Off'}
      </span>
    </span>
  )
}
