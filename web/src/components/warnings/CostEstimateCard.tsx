/**
 * CostEstimateCard Component
 *
 * Displays estimated monthly costs for third-party services in the configuration.
 * Shows service breakdown in expandable detail view.
 */

import { useState } from 'react'
import { DollarSign, ChevronDown, ChevronRight } from 'lucide-react'
import type { getCostEstimate } from '../../lib/validation'

/**
 * Props for CostEstimateCard component
 */
export interface CostEstimateCardProps {
  /** Cost estimate data from validation */
  estimate: ReturnType<typeof getCostEstimate>
  /** Additional CSS classes */
  className?: string
}

/**
 * Card displaying cost estimates with expandable service breakdown
 */
export function CostEstimateCard({ estimate, className }: CostEstimateCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  if (estimate.services.length === 0) return null

  return (
    <div
      className={`rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 p-3 ${className || ''}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <DollarSign className="h-4 w-4 text-blue-600 dark:text-blue-400 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
              Cost Estimate
            </p>
            <p className="text-xs text-blue-700 dark:text-blue-300 mt-0.5">
              {estimate.monthly > 0
                ? `$${estimate.monthly}/month + usage fees`
                : 'Starting free, pay-as-you-grow'}
            </p>
          </div>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-xs font-medium text-blue-700 dark:text-blue-300 hover:underline flex items-center gap-1"
        >
          {isExpanded ? (
            <>
              <ChevronDown className="h-3 w-3" />
              Hide
            </>
          ) : (
            <>
              <ChevronRight className="h-3 w-3" />
              Show
            </>
          )}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-3 space-y-1.5">
          {estimate.services.map((service) => (
            <div
              key={service.name}
              className="flex items-start justify-between gap-2 text-xs"
            >
              <span className="font-medium text-blue-900 dark:text-blue-100">
                {service.name}
              </span>
              <span className="text-blue-700 dark:text-blue-300 text-right">
                {service.cost > 0 ? `$${service.cost}/mo` : service.note}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
