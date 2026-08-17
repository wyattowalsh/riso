import { describe, it, expect } from 'vitest'
import {
  parseShareConfigPayload,
  parseCustomPresetsStorage,
} from '../lib/configSchemas'

describe('configSchemas', () => {
  it('remaps share payloads with known removed answer keys', () => {
    const result = parseShareConfigPayload({ api_tracks: 'python' })
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.api_module).toBe('enabled')
      expect(result.data.api_languages).toEqual(['python'])
      expect(result.data).not.toHaveProperty('api_tracks')
    }
  })

  it('rejects share payloads with leftover unmapped removed keys', () => {
    const result = parseShareConfigPayload({ saas_auth: 'firebase' })
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error).toMatch(/saas_auth/)
    }
  })

  it('accepts valid share payloads', () => {
    const result = parseShareConfigPayload({
      project_name: 'shared-app',
      api_module: 'enabled',
    })
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.project_name).toBe('shared-app')
    }
  })

  it('soft-migrates incomplete custom preset storage', () => {
    const parsed = parseCustomPresetsStorage({ bad: { foo: 1 } })
    expect(parsed.bad?.name).toBe('bad')
    expect(parsed.bad?.version).toBe(1)
  })

  it('drops non-object preset entries', () => {
    expect(parseCustomPresetsStorage({ bad: 'nope' })).toEqual({})
  })

  it('parses valid custom preset storage', () => {
    const parsed = parseCustomPresetsStorage({
      mine: {
        name: 'Mine',
        config: { project_name: 'x' },
        createdAt: '2026-01-01T00:00:00.000Z',
        version: 1,
      },
    })
    expect(parsed.mine?.name).toBe('Mine')
  })
})
