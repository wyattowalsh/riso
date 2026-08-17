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

  // Auto-scroll and move focus into the highlighted control
  useEffect(() => {
    if (!isHighlighted || !ref.current) return

    const timer = window.setTimeout(() => {
      const node = ref.current
      if (!node) return
      node.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      })
      const focusable = node.querySelector<HTMLElement>(
        'input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), [role="switch"]:not([disabled])',
      )
      focusable?.focus({ preventScroll: true })
    }, 400)

    return () => window.clearTimeout(timer)
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
