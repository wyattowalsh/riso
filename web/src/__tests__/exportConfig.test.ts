import { describe, it, expect } from 'vitest'
import {
  generateCliCommand,
  configToCopierArgs,
  shellEscapeString,
  resolveExportProjectName,
} from '../lib/exportConfig'
import type { RisoConfig } from '../lib/store'

describe('generateCliCommand', () => {
  it('includes project_name when config omits it', () => {
    const cmd = generateCliCommand({})
    expect(cmd).toContain("project_name='my-project'")
    expect(cmd).toContain("'./my-project'")
  })

  it('uses configured project_name in path and data', () => {
    const config: Partial<RisoConfig> = { project_name: 'acme-app' }
    const cmd = generateCliCommand(config)
    expect(cmd).toContain("'./acme-app'")
    expect(cmd).toContain("project_name='acme-app'")
  })

  it('shell-escapes unsafe string values', () => {
    const escaped = shellEscapeString(`it's fine`)
    expect(escaped.startsWith("'")).toBe(true)
    expect(escaped.endsWith("'")).toBe(true)
    expect(escaped).toContain('it')
  })

  it('rejects invalid project names at export', () => {
    expect(() =>
      resolveExportProjectName({ project_name: 'bad name' }),
    ).toThrow()
  })

  it('maps full-stack shaped config to copier args', () => {
    const args = configToCopierArgs({
      project_name: 'full-demo',
      api_module: 'enabled',
      api_languages: ['python'],
      docs_module: 'enabled',
      docs_framework: 'fumadocs',
    })
    expect(args.project_name).toBe('full-demo')
    expect(args.api_module).toBe('enabled')
    expect(args.docs_framework).toBe('fumadocs')
  })
})
