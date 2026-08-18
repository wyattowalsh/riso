import { describe, it, expect } from 'vitest'
import {
  canVisitStep,
  canProceedFromBasics,
  clampWizardStep,
  clampPersistedWizardStep,
  stepAfterExternalConfigApply,
  REVIEW_STEP_ID,
} from '../lib/wizardGate'

describe('wizardGate', () => {
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
    expect(canVisitStep(REVIEW_STEP_ID, 0, 'my-app')).toBe(true)
  })

  it('clampWizardStep rejects illegal forward jumps', () => {
    expect(clampWizardStep(3, 0, '')).toBe(0)
    expect(clampWizardStep(2, 0, 'valid-name')).toBe(2)
  })

  it('stepAfterExternalConfigApply forces basics without project_name', () => {
    expect(stepAfterExternalConfigApply({})).toBe(0)
    expect(stepAfterExternalConfigApply({ project_name: 'demo-app' })).toBe(
      REVIEW_STEP_ID,
    )
  })

  it('canProceedFromBasics matches project name validation', () => {
    expect(canProceedFromBasics('')).toBe(false)
    expect(canProceedFromBasics('good-project')).toBe(true)
  })

  it('clampPersistedWizardStep does not keep Review when project_name is invalid', () => {
    expect(canVisitStep(REVIEW_STEP_ID, REVIEW_STEP_ID, 'bad name')).toBe(true)
    expect(clampPersistedWizardStep(REVIEW_STEP_ID, 'bad name')).toBe(0)
    expect(clampPersistedWizardStep(REVIEW_STEP_ID, 'a')).toBe(0)
    expect(clampPersistedWizardStep(REVIEW_STEP_ID, 'good-project')).toBe(
      REVIEW_STEP_ID,
    )
  })
})
