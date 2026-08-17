import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '../test-utils'
import { ProjectBasics } from '../../components/steps/ProjectBasics'
import { generateYamlConfig } from '../../lib/exportConfig'
import { normalizeApiFeatures, useRisoStore } from '../../lib/store'

describe('ProjectBasics', () => {
  beforeEach(() => {
    localStorage.clear()
    useRisoStore.setState({
      config: { project_name: '' },
      currentStep: 0,
    })
  })

  it('announces the required name error when empty', () => {
    render(<ProjectBasics />)
    const input = screen.getByRole('textbox', { name: /project name/i })
    expect(input).toHaveAttribute('aria-invalid', 'true')
    expect(input).toHaveAttribute('aria-describedby', 'projectName-error')
    expect(screen.getByRole('alert')).toHaveTextContent('Project name is required')
  })
})

describe('normalizeApiFeatures', () => {
  it('maps matrix lists and comma strings to the toggle model', () => {
    expect(normalizeApiFeatures([])).toBe('none')
    expect(normalizeApiFeatures(['graphql'])).toBe('graphql')
    expect(normalizeApiFeatures(['graphql', 'websocket'])).toBe('graphql,websocket')
    expect(normalizeApiFeatures('websocket')).toBe('websocket')
    expect(normalizeApiFeatures('none')).toBe('none')
  })
})

describe('generateYamlConfig', () => {
  it('documents riso copy --answers-file usage', () => {
    const yaml = generateYamlConfig({ project_name: 'demo-app' })
    expect(yaml).toContain('uv run riso copy --answers-file copier-answers.yml')
    expect(yaml).not.toContain('copier copy')
  })
})

describe('updateConfig api_features coerce', () => {
  beforeEach(() => {
    localStorage.clear()
    useRisoStore.setState({
      config: { project_name: '', api_module: 'enabled' },
      currentStep: 0,
    })
  })

  it('normalizes empty api_features lists to none', () => {
    const { updateConfig } = useRisoStore.getState()
    updateConfig({
      api_features: [] as unknown as import('../../lib/store').RisoConfig['api_features'],
    })
    expect(useRisoStore.getState().config.api_features).toBe('none')
  })
})

