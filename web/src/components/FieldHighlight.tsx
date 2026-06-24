/**
 * FieldHighlight Component
 *
 * Wrapper component that highlights a field when it's the target of a search navigation.
 * Provides a smooth pulsing animation and auto-scroll functionality.
 */

import { useEffect, useRef, ReactNode } from 'react'
import { useRisoStore } from '../lib/store'
import { cn } from '../lib/utils'

interface FieldHighlightProps {
  fieldKey: string
  children: ReactNode
  className?: string
}

export function FieldHighlight({ fieldKey, children, className }: FieldHighlightProps) {
  const { highlightedField } = useRisoStore()
  const ref = useRef<HTMLDivElement>(null)
  const isHighlighted = highlightedField === fieldKey

  // Auto-scroll to highlighted field
  useEffect(() => {
    if (isHighlighted && ref.current) {
      // Small delay to ensure the step transition completes
      setTimeout(() => {
        ref.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        })
      }, 400)
    }
  }, [isHighlighted])

  return (
    <div
      ref={ref}
      className={cn(
        'transition-all duration-500',
        isHighlighted && 'animate-highlight-pulse',
        className
      )}
      data-field-key={fieldKey}
    >
      {children}
    </div>
  )
}
