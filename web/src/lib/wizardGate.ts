import { validateProjectName } from '../components/steps/ProjectBasics'
import { WIZARD_STEPS } from './wizardSteps'

export const REVIEW_STEP_ID = WIZARD_STEPS.length - 1
export const MAX_WIZARD_STEP = REVIEW_STEP_ID

export function canProceedFromBasics(projectName: string): boolean {
  return validateProjectName(projectName).valid
}

/**
 * Whether the user may navigate to `stepId` from `currentStep` given project name validity.
 */
export function canVisitStep(
  stepId: number,
  currentStep: number,
  projectName: string,
): boolean {
  if (stepId < 0 || stepId > MAX_WIZARD_STEP) {
    return false
  }
  const canProceed = canProceedFromBasics(projectName)
  return stepId <= currentStep || (stepId > 0 && canProceed)
}

export function clampWizardStep(
  step: number,
  currentStep: number,
  projectName: string,
): number {
  const bounded = Math.max(0, Math.min(MAX_WIZARD_STEP, step))
  if (!canVisitStep(bounded, currentStep, projectName)) {
    return currentStep
  }
  return bounded
}

/** After applying a preset/history payload, choose review or force basics. */
export function stepAfterExternalConfigApply(
  config: { project_name?: string },
  currentStep = 0,
): number {
  const name = config.project_name ?? ''
  if (!canProceedFromBasics(name)) {
    return 0
  }
  return canVisitStep(REVIEW_STEP_ID, currentStep, name) ? REVIEW_STEP_ID : 0
}
