import { describe, it, expect } from 'vitest'
import { REMOVED_ANSWER_KEYS } from '../lib/removedAnswerKeys'

const PYTHON_REMOVED_KEYS = [
  'api_tracks',
  'api_language',
  'docs_site',
  'mcp_language',
  'saas_starter_module',
  'saas_auth',
  'saas_billing',
  'include_admin',
] as const

describe('removedAnswerKeys parity with Python SSOT', () => {
  it('exposes exactly eight removed keys', () => {
    expect(Object.keys(REMOVED_ANSWER_KEYS)).toHaveLength(8)
  })

  it('matches Python removed_answer_keys key set', () => {
    expect(Object.keys(REMOVED_ANSWER_KEYS).sort()).toEqual(
      [...PYTHON_REMOVED_KEYS].sort(),
    )
  })
})
