/**
 * WarningItem Component
 *
 * Displays a single validation warning or error with quick-fix actions.
 * Supports collapsible details, navigation to related fields, and dismissal for info-level warnings.
 */

import { useState } from 'react'
import {
  AlertTriangle,
  AlertCircle,
  Info,
  ArrowRight,
  ChevronDown,
  ChevronRight,
  X,
  Zap,
} from 'lucide-react'
import { cn } from '../../lib/utils'
import type { Warning } from '../../lib/useValidation'

/**
 * Props for WarningItem component
 */
export interface WarningItemProps {
  /** Warning data to display */
  warning: Warning
  /** Callback to navigate to related field */
  onNavigate: (field: string) => void
  /** Callback to dismiss warning */
  onDismiss: (id: string) => void
}

/**
 * Displays a single warning with severity-based styling and interactive actions
 */
export function WarningItem({ warning, onNavigate, onDismiss }: WarningItemProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const Icon =
    warning.severity === 'error'
      ? AlertCircle
      : warning.severity === 'warning'
        ? AlertTriangle
        : Info

  const bgColor =
    warning.severity === 'error'
      ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
      : warning.severity === 'warning'
        ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800'
        : 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'

  const textColor =
    warning.severity === 'error'
      ? 'text-red-700 dark:text-red-300'
      : warning.severity === 'warning'
        ? 'text-amber-700 dark:text-amber-300'
        : 'text-blue-700 dark:text-blue-300'

  const iconColor =
    warning.severity === 'error'
      ? 'text-red-500'
      : warning.severity === 'warning'
        ? 'text-amber-500'
        : 'text-blue-500'

  const canDismiss = warning.severity === 'info'

  return (
    <div
      className={cn(
        'flex items-start gap-3 p-3 rounded-lg border transition-colors',
        bgColor
      )}
    >
      <Icon className={cn('h-4 w-4 flex-shrink-0 mt-0.5', iconColor)} />
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <p className={cn('text-sm font-medium', textColor)}>{warning.message}</p>
          {canDismiss && (
            <button
              onClick={() => onDismiss(warning.id)}
              className={cn(
                'flex-shrink-0 hover:opacity-70 transition-opacity',
                textColor
              )}
              aria-label="Dismiss warning"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {warning.details && (
          <div className="mt-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className={cn(
                'inline-flex items-center gap-1 text-xs font-medium hover:underline',
                textColor
              )}
            >
              {isExpanded ? (
                <ChevronDown className="h-3 w-3" />
              ) : (
                <ChevronRight className="h-3 w-3" />
              )}
              {isExpanded ? 'Hide' : 'Show'} details
            </button>
            {isExpanded && (
              <p className={cn('mt-1 text-xs opacity-90', textColor)}>
                {warning.details}
              </p>
            )}
          </div>
        )}

        <div className="flex items-center gap-2 mt-2 flex-wrap">
          {warning.fix && (
            <button
              onClick={warning.fix.action}
              className={cn(
                'inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors',
                warning.severity === 'error'
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : warning.severity === 'warning'
                    ? 'bg-amber-600 hover:bg-amber-700 text-white'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
              )}
            >
              <Zap className="h-3 w-3" />
              {warning.fix.label}
            </button>
          )}
          {warning.relatedField && (
            <button
              onClick={() => onNavigate(warning.relatedField!)}
              className={cn(
                'inline-flex items-center gap-1 text-xs font-medium hover:underline',
                textColor
              )}
            >
              Go to {formatFieldName(warning.relatedField)}
              <ArrowRight className="h-3 w-3" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

/**
 * Format field name for display
 * Converts snake_case to Title Case
 */
function formatFieldName(field: string): string {
  return field
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}
