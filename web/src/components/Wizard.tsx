import { useRisoStore } from '../lib/store'
import { ProjectBasics } from './steps/ProjectBasics'
import { ModulesConfig } from './steps/ModulesConfig'
import { DocsConfig } from './steps/DocsConfig'
import { SaaSConfig } from './steps/SaaSConfig'
import { AIToolsConfig } from './steps/AIToolsConfig'
import { ReviewOutput } from './steps/ReviewOutput'
import { Check } from 'lucide-react'
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
  const CurrentStepComponent = STEPS[currentStep]?.component || ProjectBasics

  return (
    <div className="space-y-8">
      {/* Step indicator */}
      <nav aria-label="Progress">
        <ol className="flex items-center justify-center">
          {STEPS.map((step, index) => (
            <li key={step.id} className={cn('relative', index !== STEPS.length - 1 && 'pr-8 sm:pr-20')}>
              {index !== STEPS.length - 1 && (
                <div
                  className="absolute top-4 left-8 -ml-px h-0.5 w-full sm:w-20 bg-gray-200/80 dark:bg-gray-700/70"
                  aria-hidden="true"
                >
                  <div
                    className={cn(
                      'h-full bg-riso-500 transition-all duration-300',
                      currentStep > index ? 'w-full' : 'w-0'
                    )}
                  />
                </div>
              )}
              <button
                onClick={() => setStep(step.id)}
                aria-current={currentStep === step.id ? 'step' : undefined}
                className={cn(
                  'group flex flex-col items-center transition-transform duration-200',
                  currentStep >= step.id ? 'cursor-pointer hover:-translate-y-0.5' : 'cursor-not-allowed'
                )}
              >
                <span
                  className={cn(
                    'flex h-8 w-8 items-center justify-center rounded-full border-2 transition-all duration-200',
                    currentStep > step.id
                      ? 'border-riso-500 bg-riso-500 text-white shadow-md shadow-riso-500/30'
                      : currentStep === step.id
                        ? 'border-riso-500 bg-white/90 dark:bg-gray-900/80 text-riso-500 ring-2 ring-riso-200/60 dark:ring-riso-500/20'
                        : 'border-gray-300 dark:border-gray-600 bg-white/70 dark:bg-gray-900/70 text-gray-500'
                  )}
                >
                  {currentStep > step.id ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <span className="text-sm font-medium">{step.id + 1}</span>
                  )}
                </span>
                <span
                  className={cn(
                    'mt-2 text-xs font-medium transition-colors',
                    currentStep >= step.id
                      ? 'text-riso-600 dark:text-riso-400'
                      : 'text-gray-500 dark:text-gray-400'
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
      <div className="riso-card p-6 sm:p-8">
        <div key={currentStep} className="animate-fade-up">
          <CurrentStepComponent />
        </div>
      </div>

      {/* Navigation buttons */}
      <div className="flex justify-between">
        <button
          onClick={() => setStep(Math.max(0, currentStep - 1))}
          disabled={currentStep === 0}
          className={cn(
            'px-6 py-2.5 rounded-lg font-medium transition-colors',
            currentStep === 0
              ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
          )}
        >
          Previous
        </button>
        <button
          onClick={() => setStep(Math.min(STEPS.length - 1, currentStep + 1))}
          disabled={currentStep === STEPS.length - 1}
          className={cn(
            'px-6 py-2.5 rounded-lg font-medium transition-colors',
            currentStep === STEPS.length - 1
              ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
              : 'bg-riso-500 text-white hover:bg-riso-600'
          )}
        >
          {currentStep === STEPS.length - 2 ? 'Generate' : 'Next'}
        </button>
      </div>
    </div>
  )
}
