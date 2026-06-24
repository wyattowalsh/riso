/**
 * QuickFixButton Component
 *
 * One-click action button to apply quick fixes to configuration issues.
 * Displays with severity-appropriate styling.
 */

import { Zap } from 'lucide-react'
import { cn } from '../../lib/utils'

/**
 * Props for QuickFixButton component
 */
export interface QuickFixButtonProps {
  /** Label text for the button */
  label: string
  /** Click handler to apply the fix */
  onClick: () => void
  /** Severity level for styling */
  severity: 'error' | 'warning' | 'info'
  /** Additional CSS classes */
  className?: string
}

/**
 * Quick-fix action button with severity-based styling
 */
export function QuickFixButton({
  label,
  onClick,
  severity,
  className,
}: QuickFixButtonProps) {
  const buttonStyles =
    severity === 'error'
      ? 'bg-red-600 hover:bg-red-700 text-white'
      : severity === 'warning'
        ? 'bg-amber-600 hover:bg-amber-700 text-white'
        : 'bg-blue-600 hover:bg-blue-700 text-white'

  return (
    <button
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors',
        buttonStyles,
        className
      )}
    >
      <Zap className="h-3 w-3" />
      {label}
    </button>
  )
}
