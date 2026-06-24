import { useState, useEffect, useRef } from 'react'
import { useRisoStore } from '../lib/store'
import { ProjectBasics } from './steps/ProjectBasics'
import { ModulesConfig } from './steps/ModulesConfig'
import { DocsConfig } from './steps/DocsConfig'
import { SaaSConfig } from './steps/SaaSConfig'
import { AIToolsConfig } from './steps/AIToolsConfig'
import { ReviewOutput } from './steps/ReviewOutput'
import { Check, ChevronLeft, ChevronRight, Sparkles } from 'lucide-react'
import { cn } from '../lib/utils'
import { WIZARD_STEPS } from '../lib/wizardSteps'

const STEPS = [
  { ...WIZARD_STEPS[0], component: ProjectBasics },
  { ...WIZARD_STEPS[1], component: ModulesConfig },
  { ...WIZARD_STEPS[2], component: DocsConfig },
  { ...WIZARD_STEPS[3], component: SaaSConfig },
  { ...WIZARD_STEPS[4], component: AIToolsConfig },
  { ...WIZARD_STEPS[5], component: ReviewOutput },
]

export function Wizard() {
  const { currentStep, setStep } = useRisoStore()
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [slideDirection, setSlideDirection] = useState<'left' | 'right'>('right')
  const prevStepRef = useRef(currentStep)
  const CurrentStepComponent = STEPS[currentStep]?.component || ProjectBasics

  // Handle step transitions with direction
  useEffect(() => {
    if (prevStepRef.current !== currentStep) {
      setSlideDirection(currentStep > prevStepRef.current ? 'right' : 'left')
      setIsTransitioning(true)
      const timer = setTimeout(() => setIsTransitioning(false), 300)
      prevStepRef.current = currentStep
      return () => clearTimeout(timer)
    }
  }, [currentStep])

  return (
    <div className="space-y-8">
      {/* Step indicator */}
      <nav aria-label="Progress" className="relative">
        {/* Background glow for active area */}
        <div className="absolute inset-0 -z-10 opacity-30 dark:opacity-20 blur-3xl">
          <div
            className="h-full bg-gradient-to-r from-riso-green via-riso-federal-blue to-riso-grape"
            style={{
              maskImage: 'radial-gradient(ellipse at center, black 0%, transparent 70%)',
              WebkitMaskImage: 'radial-gradient(ellipse at center, black 0%, transparent 70%)',
            }}
          />
        </div>

        <ol className="flex items-center justify-between w-full max-w-3xl mx-auto px-4">
          {STEPS.map((step, index) => (
            <li key={step.id} className={cn('relative flex-1', index !== STEPS.length - 1 && 'mr-2 sm:mr-0')}>
              {/* Progress line between steps */}
              {index !== STEPS.length - 1 && (
                <div
                  className="step-progress-line absolute top-5 left-1/2 h-0.5 w-full bg-gray-200/80 dark:bg-gray-700/70 rounded-full overflow-hidden"
                  aria-hidden="true"
                >
                  <div
                    className={cn(
                      'h-full transition-all duration-700 ease-out rounded-full',
                      'bg-gradient-to-r from-riso-green via-riso-teal to-riso-federal-blue',
                      currentStep > index ? 'w-full' : 'w-0'
                    )}
                    style={{
                      boxShadow: currentStep > index ? '0 0 8px rgba(0, 169, 92, 0.5)' : 'none'
                    }}
                  />
                </div>
              )}
              <button
                onClick={() => setStep(step.id)}
                aria-current={currentStep === step.id ? 'step' : undefined}
                className={cn(
                  'group flex flex-col items-center transition-all duration-300 w-full',
                  currentStep >= step.id ? 'cursor-pointer hover:-translate-y-1 hover:scale-105' : 'cursor-not-allowed opacity-60'
                )}
              >
                {/* Step circle */}
                <span
                  className={cn(
                    'step-indicator relative flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all duration-300',
                    currentStep > step.id
                      ? 'step-indicator completed border-riso-green bg-gradient-to-br from-riso-green to-riso-teal text-white shadow-lg shadow-riso-green/40'
                      : currentStep === step.id
                        ? 'step-indicator active border-riso-federal-blue bg-white dark:bg-gray-900 text-riso-federal-blue shadow-lg shadow-riso-federal-blue/30'
                        : 'border-gray-300 dark:border-gray-600 bg-white/70 dark:bg-gray-900/70 text-gray-400'
                  )}
                >
                  {currentStep > step.id ? (
                    <Check className="h-5 w-5 animate-bounce-in" />
                  ) : currentStep === step.id ? (
                    <>
                      <span className="text-sm font-bold">{step.id + 1}</span>
                      {/* Active sparkle effect */}
                      <span className="absolute -top-1 -right-1">
                        <Sparkles className="h-3 w-3 text-riso-sunflower animate-pulse" />
                      </span>
                    </>
                  ) : (
                    <span className="text-sm font-medium">{step.id + 1}</span>
                  )}
                </span>
                {/* Step label */}
                <span
                  className={cn(
                    'mt-3 text-xs transition-all duration-300 max-w-[4rem] text-center leading-tight',
                    currentStep === step.id
                      ? 'font-bold text-riso-federal-blue dark:text-riso-cornflower scale-105'
                      : currentStep > step.id
                        ? 'font-semibold text-riso-green dark:text-riso-mint'
                        : 'font-medium text-gray-400 dark:text-gray-500'
                  )}
                >
                  {step.name}
                </span>
              </button>
            </li>
          ))}
        </ol>
      </nav>

      {/* Current step content */}
      <div className="riso-card-gradient p-6 sm:p-8 overflow-hidden">
        <div
          key={currentStep}
          className={cn(
            'transition-all duration-300 ease-out',
            isTransitioning
              ? slideDirection === 'right'
                ? 'animate-slide-in-right'
                : 'animate-slide-in-left'
              : 'animate-fade-up'
          )}
        >
          <CurrentStepComponent />
        </div>
      </div>

      {/* Navigation buttons */}
      <div className="flex justify-between items-center">
        <button
          onClick={() => setStep(Math.max(0, currentStep - 1))}
          disabled={currentStep === 0}
          className={cn(
            'group flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium transition-all duration-300',
            currentStep === 0
              ? 'bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed'
              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 hover:shadow-md hover:-translate-x-1 border border-gray-200 dark:border-gray-700'
          )}
        >
          <ChevronLeft className={cn(
            'h-4 w-4 transition-transform duration-300',
            currentStep !== 0 && 'group-hover:-translate-x-1'
          )} />
          Previous
        </button>

        {/* Step indicator dots (mobile-friendly) */}
        <div className="hidden sm:flex items-center gap-2">
          {STEPS.map((_, index) => (
            <button
              key={index}
              onClick={() => index <= currentStep && setStep(index)}
              className={cn(
                'h-2 rounded-full transition-all duration-300',
                index === currentStep
                  ? 'w-6 bg-riso-federal-blue'
                  : index < currentStep
                    ? 'w-2 bg-riso-green hover:scale-125 cursor-pointer'
                    : 'w-2 bg-gray-300 dark:bg-gray-600'
              )}
              aria-label={`Go to step ${index + 1}`}
              disabled={index > currentStep}
            />
          ))}
        </div>

        <button
          onClick={() => setStep(Math.min(STEPS.length - 1, currentStep + 1))}
          disabled={currentStep === STEPS.length - 1}
          className={cn(
            'group flex items-center gap-2 transition-all duration-300',
            currentStep === STEPS.length - 1
              ? 'px-5 py-2.5 rounded-xl bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed'
              : 'btn-primary hover:translate-x-1'
          )}
        >
          {currentStep === STEPS.length - 2 ? (
            <>
              <Sparkles className="h-4 w-4" />
              Generate
            </>
          ) : (
            <>
              Next
              <ChevronRight className={cn(
                'h-4 w-4 transition-transform duration-300',
                currentStep !== STEPS.length - 1 && 'group-hover:translate-x-1'
              )} />
            </>
          )}
        </button>
      </div>
    </div>
  )
}
