import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it, expect } from 'vitest'
import { api } from '../lib/api'
import { REMOVED_ANSWER_KEYS, RemovedAnswerKeyError } from '../lib/removedAnswerKeys'

const FIXTURE_DIR = join(
  dirname(fileURLToPath(import.meta.url)),
  'fixtures/remap',
)

function fixture(name: string): string {
  return readFileSync(join(FIXTURE_DIR, name), 'utf8')
}

describe('api.importConfig / exportConfig (WEB-T02 / WEB-T03)', () => {
  it('remaps mixed 1.x YAML then fail-closes leftovers', () => {
    const imported = api.importConfig(fixture('mixed.yml'))
    expect(imported.api_module).toBe('enabled')
    expect(imported.api_languages).toEqual(['python', 'go'])
    expect(imported.mcp_languages).toEqual(['typescript'])
    expect(imported.docs_framework).toBe('docusaurus')
    expect(imported.saas_admin_dashboard).toBe(false)
    for (const key of Object.keys(REMOVED_ANSWER_KEYS)) {
      expect(imported).not.toHaveProperty(key)
    }
  })

  it('throws RemovedAnswerKeyError on leftover unmapped values', () => {
    expect(() => api.importConfig(fixture('leftover.yml'))).toThrow(
      RemovedAnswerKeyError,
    )
    expect(() => api.importConfig(fixture('leftover.yml'))).toThrow(/saas_auth/)
  })

  it('exportConfig remaps then never emits old keys', () => {
    const yaml = api.exportConfig({
      project_name: 'export-legacy',
      api_language: 'python',
      mcp_language: 'node',
    })
    expect(yaml).not.toMatch(/(?:^|\n)api_language:/)
    expect(yaml).not.toMatch(/(?:^|\n)mcp_language:/)
    expect(yaml).toContain('api_languages:')
    expect(yaml).toContain('mcp_languages:')
  })
})
