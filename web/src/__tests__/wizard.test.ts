import { describe, it, expect } from 'vitest'
import { canVisitStep } from '../lib/wizardGate'

describe('wizard step navigation gate', () => {
  it('blocks forward jumps from basics when project name is empty', () => {
    expect(canVisitStep(2, 0, '')).toBe(false)
    expect(canVisitStep(5, 0, '   ')).toBe(false)
  })

  it('allows returning to earlier steps', () => {
    expect(canVisitStep(0, 3, '')).toBe(true)
    expect(canVisitStep(1, 3, '')).toBe(true)
  })

  it('allows forward navigation once basics have a name', () => {
    expect(canVisitStep(2, 0, 'my-app')).toBe(true)
    expect(canVisitStep(5, 0, 'my-app')).toBe(true)
  })
})
