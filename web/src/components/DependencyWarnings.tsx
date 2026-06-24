/**
 * DependencyWarnings Module
 *
 * Main entry point for dependency validation and warnings.
 * Exports the refactored DependencyWarnings component and utility components.
 *
 * The main DependencyWarnings component has been refactored into focused subcomponents:
 * - WarningItem: Single warning display
 * - CostEstimateCard: Cost summary display
 * - QuickFixButton: One-click fix actions
 * - useValidation: Validation logic hook
 *
 * This file retains utility components (InlineDependencyWarning, DependencyBadge)
 * and re-exports the main component for backward compatibility.
 */

import { useMemo } from 'react'
import { AlertTriangle, AlertCircle, CheckCircle } from 'lucide-react'
import { cn } from '../lib/utils'
import { useRisoStore } from '../lib/store'
import { useValidation } from '../lib/useValidation'
import { validateDependencies } from '../lib/dependencies'

// Re-export main component and types from warnings module
export {
  DependencyWarnings,
  type DependencyWarningsProps,
} from './warnings/DependencyWarnings'

export {
  WarningItem,
  type WarningItemProps,
} from './warnings/WarningItem'

export {
  CostEstimateCard,
  type CostEstimateCardProps,
} from './warnings/CostEstimateCard'

export {
  QuickFixButton,
  type QuickFixButtonProps,
} from './warnings/QuickFixButton'

// Re-export types from validation hook
export type { Warning } from '../lib/useValidation'

/**
 * Props for InlineDependencyWarning component
 */
export interface InlineDependencyWarningProps {
  /** Field name to check for warnings */
  field: string
  /** Additional CSS classes */
  className?: string
}

/**
 * Compact inline version for use in step forms
 * Displays warnings related to a specific field
 */
export function InlineDependencyWarning({
  field,
  className,
}: InlineDependencyWarningProps) {
  const { config } = useRisoStore()
  const warnings = useMemo(() => validateDependencies(config), [config])

  const fieldWarnings = warnings.filter(
    (w) => w.field === field || w.relatedField === field
  )

  if (fieldWarnings.length === 0) return null

  const warning = fieldWarnings[0]
  const isError = warning.type === 'error'

  return (
    <div
      className={cn(
        'flex items-center gap-2 text-xs mt-1',
        isError ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400',
        className
      )}
    >
      {isError ? (
        <AlertCircle className="h-3 w-3" />
      ) : (
        <AlertTriangle className="h-3 w-3" />
      )}
      <span>{warning.message}</span>
    </div>
  )
}

/**
 * Props for DependencyBadge component
 */
export interface DependencyBadgeProps {
  /** Additional CSS classes */
  className?: string
}

/**
 * Summary badge for sidebar showing validation status
 * Displays error count, warning count, or success indicator
 * Uses useValidation hook for consistent counting with DependencyWarnings
 */
export function DependencyBadge({ className }: DependencyBadgeProps) {
  const { config, updateConfig } = useRisoStore()
  const { warnings, errors: errorList } = useValidation(config, updateConfig)

  const errorCount = errorList.length
  const totalCount = warnings.length

  if (totalCount === 0) {
    return (
      <span
        className={cn(
          'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-riso-green/10 text-riso-green dark:text-riso-mint',
          className
        )}
      >
        <CheckCircle className="h-3 w-3" />
        Valid
      </span>
    )
  }

  if (errorCount > 0) {
    return (
      <span
        className={cn(
          'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300',
          className
        )}
      >
        <AlertCircle className="h-3 w-3" />
        {errorCount} {errorCount === 1 ? 'issue' : 'issues'}
      </span>
    )
  }

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300',
        className
      )}
    >
      <AlertTriangle className="h-3 w-3" />
      {totalCount} {totalCount === 1 ? 'recommendation' : 'recommendations'}
    </span>
  )
}
