/**
 * Warnings Module Index
 *
 * Exports all warning-related components and utilities.
 * Provides a single import point for the warnings system.
 */

export { DependencyWarnings } from './DependencyWarnings'
export type { DependencyWarningsProps } from './DependencyWarnings'

export { WarningItem } from './WarningItem'
export type { WarningItemProps } from './WarningItem'

export { CostEstimateCard } from './CostEstimateCard'
export type { CostEstimateCardProps } from './CostEstimateCard'

export { QuickFixButton } from './QuickFixButton'
export type { QuickFixButtonProps } from './QuickFixButton'

// Re-export inline and badge components that remain in original file
// These will be moved from the original DependencyWarnings.tsx
