/**
 * DependencyWarnings Component (Refactored - Slim Orchestrator)
 *
 * Orchestrates validation warnings display by coordinating subcomponents.
 * Delegates rendering to focused components while managing state and navigation.
 */

import { useState } from 'react'
import { CheckCircle, ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react'
import { cn } from '../../lib/utils'
import { useRisoStore } from '../../lib/store'
import { useValidation } from '../../lib/useValidation'
import { WarningItem } from './WarningItem'
import { CostEstimateCard } from './CostEstimateCard'

/**
 * Props for DependencyWarnings component
 */
export interface DependencyWarningsProps {
  /** Whether to show a success message when no warnings exist */
  showEmpty?: boolean
  /** Additional CSS classes */
  className?: string
  /** Callback when navigating to a step */
  onNavigateToStep?: (step: number) => void
}

/**
 * Main orchestrator for displaying validation warnings and cost estimates
 */
export function DependencyWarnings({
  showEmpty = false,
  className,
  onNavigateToStep,
}: DependencyWarningsProps) {
  const { config, setCurrentStep, updateConfig } = useRisoStore()
  const [dismissedIds, setDismissedIds] = useState<Set<string>>(new Set())
  const [isExpanded, setIsExpanded] = useState(false)
  const [userToggled, setUserToggled] = useState(false)

  // Use validation hook for all validation logic
  const { warnings, errors, warningList, infos, costEstimate } = useValidation(
    config,
    updateConfig,
    dismissedIds
  )

  // Handle navigation to related field
  const handleNavigate = (field: string) => {
    const step = getStepForField(field)
    setCurrentStep(step)
    onNavigateToStep?.(step)
  }

  // Handle dismissing warnings
  const handleDismiss = (id: string) => {
    setDismissedIds((prev) => new Set(prev).add(id))
  }

  // Show success state when no warnings
  if (warnings.length === 0) {
    if (showEmpty) {
      return (
        <div className={cn('space-y-3', className)}>
          <div className="flex items-center gap-2 p-3 rounded-lg bg-riso-hunter-green/10 dark:bg-riso-mint/10 border border-riso-hunter-green/25 dark:border-riso-mint/20">
            <CheckCircle className="h-4 w-4 text-riso-hunter-green dark:text-riso-mint flex-shrink-0" />
            <span className="text-sm text-riso-hunter-green dark:text-riso-mint">
              Configuration is valid. No dependency issues detected.
            </span>
          </div>
          {costEstimate.services.length > 0 && (
            <CostEstimateCard estimate={costEstimate} />
          )}
        </div>
      )
    }
    return null
  }

  const totalCount = warnings.length
  const hasErrors = errors.length > 0
  const expanded = userToggled ? isExpanded : hasErrors || isExpanded
  const heading =
    hasErrors
      ? `${errors.length} ${errors.length === 1 ? 'issue' : 'issues'}`
      : `${totalCount} ${totalCount === 1 ? 'recommendation' : 'recommendations'}`

  return (
    <div
      className={cn('space-y-3', className)}
      role={hasErrors ? 'alert' : undefined}
    >
      {/* Collapsible Header */}
      <button
        type="button"
        aria-expanded={expanded}
        onClick={() => {
          setUserToggled(true)
          setIsExpanded(!expanded)
        }}
        className={cn(
          'w-full flex items-center justify-between p-3 rounded-xl border transition-colors',
          hasErrors
            ? 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800/60 hover:bg-red-100 dark:hover:bg-red-950/50'
            : 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800/50 hover:bg-amber-100 dark:hover:bg-amber-900/30',
        )}
      >
        <div className="flex items-center gap-2">
          <AlertTriangle
            className={cn(
              'h-4 w-4',
              hasErrors ? 'text-red-700 dark:text-red-300' : 'text-amber-600 dark:text-amber-400',
            )}
          />
          <span
            className={cn(
              'text-sm font-medium',
              hasErrors ? 'text-red-800 dark:text-red-200' : 'text-amber-800 dark:text-amber-200',
            )}
          >
            {heading}
          </span>
          {hasErrors && warningList.length + infos.length > 0 && (
            <span className="px-1.5 py-0.5 text-xs font-medium bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 rounded">
              {warningList.length + infos.length} more
            </span>
          )}
        </div>
        {expanded ? (
          <ChevronUp className={cn('h-4 w-4', hasErrors ? 'text-red-700 dark:text-red-300' : 'text-amber-600 dark:text-amber-400')} />
        ) : (
          <ChevronDown className={cn('h-4 w-4', hasErrors ? 'text-red-700 dark:text-red-300' : 'text-amber-600 dark:text-amber-400')} />
        )}
      </button>

      {/* Expanded Content */}
      {expanded && (
        <>
          {errors.length > 0 && (
            <div className="space-y-2">
              {errors.map((warning) => (
                <WarningItem
                  key={warning.id}
                  warning={warning}
                  onNavigate={handleNavigate}
                  onDismiss={handleDismiss}
                />
              ))}
            </div>
          )}

          {warningList.length > 0 && (
            <div className="space-y-2">
              {warningList.map((warning) => (
                <WarningItem
                  key={warning.id}
                  warning={warning}
                  onNavigate={handleNavigate}
                  onDismiss={handleDismiss}
                />
              ))}
            </div>
          )}

          {infos.length > 0 && (
            <div className="space-y-2">
              {infos.map((warning) => (
                <WarningItem
                  key={warning.id}
                  warning={warning}
                  onNavigate={handleNavigate}
                  onDismiss={handleDismiss}
                />
              ))}
            </div>
          )}
        </>
      )}

      {costEstimate.services.length > 0 && (
        <CostEstimateCard estimate={costEstimate} />
      )}
    </div>
  )
}

/**
 * Determine which wizard step corresponds to a field
 */
function getStepForField(field: string): number {
  if (field.startsWith('saas_')) return 3
  if (field.startsWith('fumadocs_') || field.startsWith('docusaurus_')) return 2
  if (field.startsWith('ai_tools_')) return 4
  if (
    field.includes('module') ||
    field === 'cli_languages' ||
    field === 'api_languages' ||
    field === 'mcp_languages'
  )
    return 1

  return 0
}
