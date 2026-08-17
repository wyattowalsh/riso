import { Sparkles, BookOpen } from 'lucide-react'
import { useRisoStore } from '../lib/store'
import { WIZARD_STEPS } from '../lib/wizardSteps'
import { canVisitStep } from '../lib/wizardGate'
import { ContextualCard } from './sidebar/ContextualCard'

export function SidebarSummary() {
  const { currentStep, setStep, config } = useRisoStore()
  const projectName = config.project_name ?? ''
  const reviewStep = WIZARD_STEPS.length - 1
  const canJumpToReview = canVisitStep(reviewStep, currentStep, projectName)

  const handleJumpToReview = () => {
    if (canJumpToReview) {
      setStep(reviewStep)
      return
    }
    if (currentStep !== 0) {
      setStep(0)
    }
    window.setTimeout(() => {
      document.getElementById('projectName')?.focus()
    }, 80)
  }

  return (
    <aside className="space-y-4 lg:sticky lg:top-24 lg:z-10">
      {/* Single Contextual Card - No redundant progress indicators */}
      <div className="riso-card p-4 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm">
        {/* Contextual Content Only */}
        <ContextualCard currentStep={currentStep} />
      </div>

      {/* Quick Actions - Always visible */}
      <div className="riso-card-soft p-4 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm">
        <div className="flex flex-col gap-2">
          <button
            type="button"
            onClick={handleJumpToReview}
            title={
              canJumpToReview
                ? undefined
                : 'Enter a valid project name to jump to review'
            }
            className="btn-primary text-xs py-2"
          >
            <Sparkles className="h-3.5 w-3.5" />
            Jump to Review
          </button>
          <a href="/docs/" className="btn-secondary text-xs py-2">
            <BookOpen className="h-3.5 w-3.5" />
            Read the Docs
          </a>
        </div>
      </div>
    </aside>
  )
}
