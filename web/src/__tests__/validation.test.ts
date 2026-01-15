import { describe, it, expect } from 'vitest'
import { validateProjectName } from '../components/steps/ProjectBasics'

describe('validateProjectName', () => {
  it('rejects empty names', () => {
    expect(validateProjectName('').valid).toBe(false)
    expect(validateProjectName('  ').valid).toBe(false)
  })

  it('rejects names shorter than 2 characters', () => {
    const result = validateProjectName('a')
    expect(result.valid).toBe(false)
    expect(result.error).toContain('at least 2 characters')
  })

  it('rejects names longer than 64 characters', () => {
    const longName = 'a'.repeat(65)
    const result = validateProjectName(longName)
    expect(result.valid).toBe(false)
    expect(result.error).toContain('64 characters')
  })

  it('rejects names starting with a number', () => {
    const result = validateProjectName('123project')
    expect(result.valid).toBe(false)
    expect(result.error).toContain('start with a letter')
  })

  it('rejects names with spaces', () => {
    const result = validateProjectName('my project')
    expect(result.valid).toBe(false)
  })

  it('rejects names with special characters', () => {
    expect(validateProjectName('my@project').valid).toBe(false)
    expect(validateProjectName('my.project').valid).toBe(false)
    expect(validateProjectName('my project!').valid).toBe(false)
  })

  it('accepts valid names with letters only', () => {
    expect(validateProjectName('myproject').valid).toBe(true)
    expect(validateProjectName('MyProject').valid).toBe(true)
  })

  it('accepts names with hyphens', () => {
    expect(validateProjectName('my-project').valid).toBe(true)
    expect(validateProjectName('my-awesome-project').valid).toBe(true)
  })

  it('accepts names with underscores', () => {
    expect(validateProjectName('my_project').valid).toBe(true)
    expect(validateProjectName('my_awesome_project').valid).toBe(true)
  })

  it('accepts names with numbers after first character', () => {
    expect(validateProjectName('project123').valid).toBe(true)
    expect(validateProjectName('my-project-2').valid).toBe(true)
  })

  it('accepts mixed valid characters', () => {
    expect(validateProjectName('My-Project_123').valid).toBe(true)
    expect(validateProjectName('awesome_project-v2').valid).toBe(true)
  })
})
