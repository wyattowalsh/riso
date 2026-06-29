import { describe, it, expect } from 'vitest'
import { validateProjectName } from '../components/steps/ProjectBasics'

/** Mirrors Wizard.tsx canVisitStep gate for unit testing without rendering. */
function canVisitStep(
  stepId: number,
  currentStep: number,
  projectName: string,
): boolean {
  const canProceedFromBasics = validateProjectName(projectName).valid
  return stepId <= currentStep || (stepId > 0 && canProceedFromBasics)
}

describe('wizard step navigation gate', () => {
  it('blocks forward jumps from basics when project name is invalid', () => {
    expect(canVisitStep(2, 0, '')).toBe(false)
    expect(canVisitStep(5, 0, 'a')).toBe(false)
  })

  it('allows returning to earlier steps', () => {
    expect(canVisitStep(0, 3, '')).toBe(true)
    expect(canVisitStep(1, 3, '')).toBe(true)
  })

  it('allows forward navigation once basics are valid', () => {
    expect(canVisitStep(2, 0, 'my-app')).toBe(true)
    expect(canVisitStep(5, 0, 'my-app')).toBe(true)
  })
})