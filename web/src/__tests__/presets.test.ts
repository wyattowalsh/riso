import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { parse as parseYAML } from 'yaml'
import {
  saveCustomPreset,
  loadCustomPresets,
  deleteCustomPreset,
  exportPresetYAML,
  importPresetYAML,
  generateShareableURL,
  parseShareableURL,
  type CustomPreset,
} from '../lib/presets'
import type { RisoConfig } from '../lib/store'

const CUSTOM_PRESETS_KEY = 'riso-custom-presets'

describe('Preset System', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    localStorage.clear()
  })

  // ========================================
  // test_save_custom_preset
  // ========================================
  describe('saveCustomPreset', () => {
    it('should save a custom preset to localStorage', () => {
      const config: Partial<RisoConfig> = {
        project_name: 'test-project',
        project_layout: 'monorepo',
        api_module: 'enabled',
        api_languages: ['python'],
      }

      saveCustomPreset('My Preset', config, 'Test description')

      const stored = localStorage.getItem(CUSTOM_PRESETS_KEY)
      expect(stored).toBeTruthy()

      const presets = JSON.parse(stored!)
      expect(presets['My Preset']).toBeDefined()
      expect(presets['My Preset'].name).toBe('My Preset')
      expect(presets['My Preset'].description).toBe('Test description')
      expect(presets['My Preset'].config).toEqual(config)
    })

    it('should save preset with version and createdAt timestamp', () => {
      const config: Partial<RisoConfig> = {
        project_name: 'version-test',
      }

      const beforeTime = new Date().toISOString()
      saveCustomPreset('Versioned Preset', config)
      const afterTime = new Date().toISOString()

      const presets = loadCustomPresets()
      const preset = presets['Versioned Preset']

      expect(preset.version).toBe(1)
      expect(preset.createdAt >= beforeTime).toBe(true)
      expect(preset.createdAt <= afterTime).toBe(true)
    })

    it('should overwrite existing preset with same name', () => {
      const config1: Partial<RisoConfig> = { project_name: 'project-1' }
      const config2: Partial<RisoConfig> = { project_name: 'project-2' }

      saveCustomPreset('Same Name', config1)
      const firstCreatedAt = loadCustomPresets()['Same Name'].createdAt

      // Small delay to ensure different timestamps
      vi.useFakeTimers()
      vi.advanceTimersByTime(1000)

      saveCustomPreset('Same Name', config2)

      vi.useRealTimers()

      const presets = loadCustomPresets()
      expect(presets['Same Name'].config.project_name).toBe('project-2')
      // Verify createdAt was updated (timestamp should be later than first save)
      expect(new Date(presets['Same Name'].createdAt).getTime()).toBeGreaterThan(new Date(firstCreatedAt).getTime())
    })

    it('should preserve other presets when saving new one', () => {
      const config1: Partial<RisoConfig> = { project_name: 'project-1' }
      const config2: Partial<RisoConfig> = { project_name: 'project-2' }

      saveCustomPreset('Preset 1', config1)
      saveCustomPreset('Preset 2', config2)

      const presets = loadCustomPresets()
      expect(Object.keys(presets)).toHaveLength(2)
      expect(presets['Preset 1']).toBeDefined()
      expect(presets['Preset 2']).toBeDefined()
    })

    it('should handle optional description', () => {
      const config: Partial<RisoConfig> = { project_name: 'no-desc' }

      saveCustomPreset('No Description', config)

      const presets = loadCustomPresets()
      expect(presets['No Description'].description).toBeUndefined()
    })

    it('should handle empty config', () => {
      const config: Partial<RisoConfig> = {}

      saveCustomPreset('Empty Config', config)

      const presets = loadCustomPresets()
      expect(presets['Empty Config'].config).toEqual({})
    })
  })

  // ========================================
  // test_load_custom_presets
  // ========================================
  describe('loadCustomPresets', () => {
    it('should return empty object when no presets stored', () => {
      const presets = loadCustomPresets()
      expect(presets).toEqual({})
    })

    it('should load all custom presets from localStorage', () => {
      const config1: Partial<RisoConfig> = { project_name: 'project-1' }
      const config2: Partial<RisoConfig> = { project_name: 'project-2' }

      saveCustomPreset('Preset 1', config1)
      saveCustomPreset('Preset 2', config2)

      const presets = loadCustomPresets()
      expect(Object.keys(presets)).toHaveLength(2)
      expect(presets['Preset 1'].config.project_name).toBe('project-1')
      expect(presets['Preset 2'].config.project_name).toBe('project-2')
    })

    it('should return empty object on corrupted localStorage data', () => {
      localStorage.setItem(CUSTOM_PRESETS_KEY, 'invalid json {')

      const presets = loadCustomPresets()
      expect(presets).toEqual({})
    })

    it('should preserve preset structure including metadata', () => {
      const config: Partial<RisoConfig> = {
        project_name: 'test',
        api_module: 'enabled',
      }

      saveCustomPreset('Full Preset', config, 'A full preset')

      const presets = loadCustomPresets()
      const preset = presets['Full Preset']

      expect(preset).toHaveProperty('name')
      expect(preset).toHaveProperty('description')
      expect(preset).toHaveProperty('config')
      expect(preset).toHaveProperty('createdAt')
      expect(preset).toHaveProperty('version')
    })

    it('should return correct type as CustomPreset', () => {
      const config: Partial<RisoConfig> = { project_name: 'typed-test' }
      saveCustomPreset('Typed', config)

      const presets = loadCustomPresets()
      const preset = presets['Typed']

      expect(typeof preset.name).toBe('string')
      expect(typeof preset.config).toBe('object')
      expect(typeof preset.createdAt).toBe('string')
      expect(typeof preset.version).toBe('number')
    })

    it('should handle multiple loads without mutation', () => {
      const config: Partial<RisoConfig> = { project_name: 'immutable' }
      saveCustomPreset('Immutable', config)

      const presets1 = loadCustomPresets()
      const presets2 = loadCustomPresets()

      expect(presets1).toEqual(presets2)
      expect(presets1['Immutable']).not.toBe(presets2['Immutable'])
    })
  })

  // ========================================
  // test_delete_custom_preset
  // ========================================
  describe('deleteCustomPreset', () => {
    it('should delete existing preset and return true', () => {
      const config: Partial<RisoConfig> = { project_name: 'delete-me' }
      saveCustomPreset('To Delete', config)

      const result = deleteCustomPreset('To Delete')

      expect(result).toBe(true)
      const presets = loadCustomPresets()
      expect(presets['To Delete']).toBeUndefined()
    })

    it('should return false when deleting non-existent preset', () => {
      const result = deleteCustomPreset('Does Not Exist')
      expect(result).toBe(false)
    })

    it('should preserve other presets when deleting one', () => {
      const config1: Partial<RisoConfig> = { project_name: 'keep-1' }
      const config2: Partial<RisoConfig> = { project_name: 'keep-2' }
      const config3: Partial<RisoConfig> = { project_name: 'delete' }

      saveCustomPreset('Keep 1', config1)
      saveCustomPreset('Keep 2', config2)
      saveCustomPreset('Delete', config3)

      deleteCustomPreset('Delete')

      const presets = loadCustomPresets()
      expect(Object.keys(presets)).toHaveLength(2)
      expect(presets['Keep 1']).toBeDefined()
      expect(presets['Keep 2']).toBeDefined()
    })

    it('should update localStorage after deletion', () => {
      const config: Partial<RisoConfig> = { project_name: 'test' }
      saveCustomPreset('Deletable', config)

      deleteCustomPreset('Deletable')

      const stored = localStorage.getItem(CUSTOM_PRESETS_KEY)
      const presets = JSON.parse(stored || '{}')
      expect(presets['Deletable']).toBeUndefined()
    })

    it('should handle case-sensitive deletion', () => {
      const config: Partial<RisoConfig> = { project_name: 'case-test' }
      saveCustomPreset('Preset', config)

      const result = deleteCustomPreset('preset') // lowercase
      expect(result).toBe(false)

      const presets = loadCustomPresets()
      expect(presets['Preset']).toBeDefined()
    })

    it('should handle deletion from empty presets', () => {
      const result = deleteCustomPreset('Non Existent')
      expect(result).toBe(false)
    })
  })

  // ========================================
  // test_export_preset_yaml
  // ========================================
  describe('exportPresetYAML', () => {
    it('should export preset to valid YAML string', () => {
      const preset: CustomPreset = {
        name: 'Export Test',
        description: 'A test preset',
        config: {
          project_name: 'test-project',
          api_module: 'enabled',
        },
        createdAt: '2024-01-01T00:00:00.000Z',
        version: 1,
      }

      const yaml = exportPresetYAML(preset)

      expect(yaml).toBeTruthy()
      expect(typeof yaml).toBe('string')
      expect(yaml).toContain('name:')
      expect(yaml).toContain('description:')
      expect(yaml).toContain('version:')
      expect(yaml).toContain('config:')
    })

    it('should include all preset fields in YAML', () => {
      const preset: CustomPreset = {
        name: 'Full Export',
        description: 'Complete preset',
        config: {
          project_name: 'full-project',
          project_layout: 'monorepo',
          api_module: 'enabled',
        },
        createdAt: '2024-01-01T00:00:00.000Z',
        version: 1,
      }

      const yaml = exportPresetYAML(preset)

      expect(yaml).toContain('name:')
      expect(yaml).toContain('Full Export')
      expect(yaml).toContain('Complete preset')
      expect(yaml).toContain('version:')
      expect(yaml).toContain('config:')
      expect(yaml).toContain('project_name:')
      expect(yaml).toContain('full-project')
    })

    it('should handle preset without description', () => {
      const preset: CustomPreset = {
        name: 'No Description',
        config: { project_name: 'test' },
        createdAt: '2024-01-01T00:00:00.000Z',
        version: 1,
      }

      const yaml = exportPresetYAML(preset)

      expect(yaml).toContain('name:')
      expect(yaml).toContain('version:')
      expect(yaml).toContain('config:')
    })

    it('should handle complex config with nested values', () => {
      const preset: CustomPreset = {
        name: 'Complex',
        description: 'Complex config',
        config: {
          project_name: 'complex-project',
          project_layout: 'monorepo',
          api_module: 'enabled',
          api_languages: ['python'],
          api_features: 'graphql,websocket',
          docs_module: 'enabled',
          docs_framework: 'fumadocs',
          fumadocs_theme: 'ocean',
        },
        createdAt: '2024-01-01T00:00:00.000Z',
        version: 1,
      }

      const yaml = exportPresetYAML(preset)

      expect(yaml).toContain('api_languages:')
      expect(yaml).toContain('fumadocs_theme: ocean')
    })

    it('should produce YAML that can be parsed back', () => {
      const preset: CustomPreset = {
        name: 'Roundtrip',
        description: 'For roundtrip test',
        config: { project_name: 'roundtrip-project' },
        createdAt: '2024-01-01T00:00:00.000Z',
        version: 1,
      }

      const yaml = exportPresetYAML(preset)
      const parsed = parseYAML(yaml)

      expect(parsed.name).toBe('Roundtrip')
      expect(parsed.description).toBe('For roundtrip test')
      expect(parsed.version).toBe(1)
      expect(parsed.config.project_name).toBe('roundtrip-project')
    })
  })

  // ========================================
  // test_import_preset_yaml
  // ========================================
  describe('importPresetYAML', () => {
    it('rejects removed Copier answer keys', () => {
      const yaml = `
name: Legacy Preset
config:
  api_tracks: python+node
`
      expect(() => importPresetYAML(yaml)).toThrow(/api_tracks/)
    })

    it('should import preset from YAML string', () => {
      const yaml = `
name: Imported Preset
description: A preset imported from YAML
version: 1
config:
  project_name: imported-project
  api_module: enabled
`

      const preset = importPresetYAML(yaml)

      expect(preset.name).toBe('Imported Preset')
      expect(preset.description).toBe('A preset imported from YAML')
      expect(preset.version).toBe(1)
      expect(preset.config.project_name).toBe('imported-project')
      expect(preset.config.api_module).toBe('enabled')
    })

    it('should set default name if not provided', () => {
      const yaml = `
config:
  project_name: unnamed
`

      const preset = importPresetYAML(yaml)

      expect(preset.name).toBe('Imported Preset')
    })

    it('should set createdAt to current time', () => {
      const yaml = `
name: Date Test
config:
  project_name: date-test
`

      const before = new Date().toISOString()
      const preset = importPresetYAML(yaml)
      const after = new Date().toISOString()

      expect(preset.createdAt >= before).toBe(true)
      expect(preset.createdAt <= after).toBe(true)
    })

    it('should default to version 1 if not specified', () => {
      const yaml = `
name: No Version
config:
  project_name: no-version
`

      const preset = importPresetYAML(yaml)

      expect(preset.version).toBe(1)
    })

    it('should handle empty config', () => {
      const yaml = `
name: Empty Config
`

      const preset = importPresetYAML(yaml)

      expect(preset.name).toBe('Empty Config')
      expect(preset.config).toBeDefined()
    })

    it('should use entire YAML as config if no config field', () => {
      const yaml = `
project_name: project-from-root
api_module: enabled
`

      const preset = importPresetYAML(yaml)

      expect(preset.config.project_name).toBe('project-from-root')
      expect(preset.config.api_module).toBe('enabled')
    })

    it('should handle YAML with special characters', () => {
      const yaml = `
name: Special & Chars
description: "Test with 'quotes' and \\"escaped\\""
config:
  project_name: special-project
`

      const preset = importPresetYAML(yaml)

      expect(preset.name).toBe('Special & Chars')
      expect(preset.description).toContain('quotes')
    })

    it('should roundtrip: export then import', () => {
      const original: CustomPreset = {
        name: 'Roundtrip Test',
        description: 'Testing export and import',
        config: {
          project_name: 'roundtrip',
          api_module: 'enabled',
          api_languages: ['python'],
        },
        createdAt: '2024-01-01T00:00:00.000Z',
        version: 1,
      }

      const yaml = exportPresetYAML(original)
      const imported = importPresetYAML(yaml)

      expect(imported.name).toBe(original.name)
      expect(imported.description).toBe(original.description)
      expect(imported.version).toBe(original.version)
      expect(imported.config).toEqual(original.config)
    })
  })

  // ========================================
  // test_shareable_url_generation
  // ========================================
  describe('generateShareableURL', () => {
    it('should generate a shareable URL with encoded config', () => {
      const config: Partial<RisoConfig> = {
        project_name: 'share-test',
        api_module: 'enabled',
      }

      const url = generateShareableURL(config)

      expect(url).toBeTruthy()
      expect(typeof url).toBe('string')
      expect(url).toContain('?preset=')
    })

    it('should include window origin in URL', () => {
      const config: Partial<RisoConfig> = { project_name: 'origin-test' }
      const url = generateShareableURL(config)

      expect(url).toContain(window.location.origin)
      expect(url).toContain(window.location.pathname)
    })

    it('should encode config as base64', () => {
      const config: Partial<RisoConfig> = { project_name: 'encoding-test' }
      const url = generateShareableURL(config)

      const paramMatch = url.match(/preset=([^&]+)/)
      expect(paramMatch).toBeTruthy()

      const encoded = paramMatch![1]
      const decoded = JSON.parse(atob(decodeURIComponent(encoded)))

      expect(decoded.project_name).toBe('encoding-test')
    })

    it('should handle complex config', () => {
      const config: Partial<RisoConfig> = {
        project_name: 'complex',
        project_layout: 'monorepo',
        api_module: 'enabled',
        api_languages: ['python'],
        api_features: 'graphql,websocket',
        docs_module: 'enabled',
        docs_framework: 'fumadocs',
        fumadocs_theme: 'ocean',
        saas_infra_module: 'enabled',
        saas_runtime: 'nextjs-16',
      }

      const url = generateShareableURL(config)

      expect(url).toContain('preset=')
      const paramMatch = url.match(/preset=([^&]+)/)
      const encoded = paramMatch![1]
      const decoded = JSON.parse(atob(decodeURIComponent(encoded)))

      expect(decoded.project_name).toBe('complex')
      expect(decoded.api_languages).toEqual(['python'])
      expect(decoded.saas_runtime).toBe('nextjs-16')
    })

    it('should handle empty config', () => {
      const config: Partial<RisoConfig> = {}
      const url = generateShareableURL(config)

      expect(url).toContain('preset=')
    })

    it('should handle special characters in project name', () => {
      const config: Partial<RisoConfig> = {
        project_name: 'project-with-special_chars.test',
      }

      const url = generateShareableURL(config)
      const paramMatch = url.match(/preset=([^&]+)/)
      const encoded = paramMatch![1]
      const decoded = JSON.parse(atob(decodeURIComponent(encoded)))

      expect(decoded.project_name).toBe('project-with-special_chars.test')
    })

    it('should be URL-safe', () => {
      const config: Partial<RisoConfig> = { project_name: 'url-safe' }
      const url = generateShareableURL(config)

      // Should not contain unencoded special characters that break URLs
      expect(url).not.toMatch(/\s/)
      expect(() => new URL(url)).not.toThrow()
    })
  })

  // ========================================
  // test_shareable_url_parsing
  // ========================================
  describe('parseShareableURL', () => {
    it('should parse shareable URL back to config', () => {
      const originalConfig: Partial<RisoConfig> = {
        project_name: 'parse-test',
        api_module: 'enabled',
      }

      const url = generateShareableURL(originalConfig)
      const parsed = parseShareableURL(url)

      expect(parsed).toEqual(originalConfig)
    })

    it('should return null when no preset parameter', () => {
      const url = 'http://localhost:3000/wizard'
      const parsed = parseShareableURL(url)

      expect(parsed).toBeNull()
    })

    it('should return null for invalid URL', () => {
      const parsed = parseShareableURL('not a valid url')

      expect(parsed).toBeNull()
    })

    it('should return null for malformed base64', () => {
      const url = 'http://localhost:3000/wizard?preset=!!!invalid!!!'
      const parsed = parseShareableURL(url)

      expect(parsed).toBeNull()
    })

    it('should handle complex config roundtrip', () => {
      const originalConfig: Partial<RisoConfig> = {
        project_name: 'complex-roundtrip',
        project_layout: 'monorepo',
        api_module: 'enabled',
        api_languages: ['python'],
        api_features: 'graphql,websocket',
        docs_module: 'enabled',
        docs_framework: 'fumadocs',
        fumadocs_theme: 'ocean',
        saas_infra_module: 'enabled',
        saas_runtime: 'nextjs-16',
        saas_hosting: 'vercel',
        saas_database: 'neon',
      }

      const url = generateShareableURL(originalConfig)
      const parsed = parseShareableURL(url)

      expect(parsed).toEqual(originalConfig)
      expect(parsed?.saas_runtime).toBe('nextjs-16')
      expect(parsed?.saas_database).toBe('neon')
    })

    it('should ignore other URL parameters', () => {
      const originalConfig: Partial<RisoConfig> = { project_name: 'test' }
      const url = generateShareableURL(originalConfig)
      const urlWithOtherParams = url + '&foo=bar&baz=qux'

      const parsed = parseShareableURL(urlWithOtherParams)

      expect(parsed).toEqual(originalConfig)
    })

    it('should handle URL with hash', () => {
      const originalConfig: Partial<RisoConfig> = { project_name: 'hash-test' }
      const url = generateShareableURL(originalConfig) + '#section'

      const parsed = parseShareableURL(url)

      expect(parsed).toEqual(originalConfig)
    })

    it('should handle encoded special characters', () => {
      const originalConfig: Partial<RisoConfig> = {
        project_name: 'special-chars_test.v1',
      }

      const url = generateShareableURL(originalConfig)
      const parsed = parseShareableURL(url)

      expect(parsed?.project_name).toBe('special-chars_test.v1')
    })
  })

  // ========================================
  // test_preset_version_migration
  // ========================================
  describe('Preset Version Migration', () => {
    it('should handle v1 preset format', () => {
      const v1Preset: CustomPreset = {
        name: 'v1 Preset',
        description: 'Version 1 preset',
        config: {
          project_name: 'v1-project',
          api_module: 'enabled',
        },
        createdAt: '2024-01-01T00:00:00.000Z',
        version: 1,
      }

      const yaml = exportPresetYAML(v1Preset)
      const imported = importPresetYAML(yaml)

      expect(imported.version).toBe(1)
      expect(imported.name).toBe('v1 Preset')
    })

    it('should maintain backward compatibility with older presets', () => {
      const oldPresetData = {
        'Old Preset': {
          name: 'Old Preset',
          config: { project_name: 'old-project' },
          createdAt: '2023-01-01T00:00:00.000Z',
          version: 1,
        },
      }

      localStorage.setItem(CUSTOM_PRESETS_KEY, JSON.stringify(oldPresetData))

      const presets = loadCustomPresets()
      expect(presets['Old Preset']).toBeDefined()
      expect(presets['Old Preset'].config.project_name).toBe('old-project')
    })

    it('should add missing fields when importing old format', () => {
      const minimialYAML = `
name: Minimal
config:
  project_name: minimal
`

      const preset = importPresetYAML(minimialYAML)

      expect(preset.name).toBe('Minimal')
      expect(preset.version).toBe(1) // Default
      expect(preset.createdAt).toBeTruthy() // Current time
      expect(preset.config).toBeDefined()
    })

    it('should handle missing version field', () => {
      const noVersionYAML = `
name: No Version
description: Test
config:
  project_name: no-version
`

      const preset = importPresetYAML(noVersionYAML)

      expect(preset.version).toBe(1)
    })

    it('should preserve version on export and import', () => {
      const preset: CustomPreset = {
        name: 'Versioned',
        config: { project_name: 'versioned' },
        createdAt: '2024-01-01T00:00:00.000Z',
        version: 2,
      }

      const yaml = exportPresetYAML(preset)
      const imported = importPresetYAML(yaml)

      expect(imported.version).toBe(2)
    })

    it('should migrate preset in localStorage', () => {
      // Simulate old preset format
      const oldData = {
        'Old Preset': {
          name: 'Old Preset',
          config: { project_name: 'old' },
          createdAt: '2023-01-01T00:00:00.000Z',
          // Note: version field might be missing
        },
      }

      localStorage.setItem(CUSTOM_PRESETS_KEY, JSON.stringify(oldData))

      // Load and re-save to migrate
      const loaded = loadCustomPresets()
      saveCustomPreset('Old Preset', loaded['Old Preset'].config, loaded['Old Preset'].description)

      const migrated = loadCustomPresets()
      expect(migrated['Old Preset'].version).toBeGreaterThanOrEqual(1)
    })

    it('should handle migration of multiple presets', () => {
      const oldData = {
        'Preset 1': {
          name: 'Preset 1',
          config: { project_name: 'project-1' },
          createdAt: '2023-01-01T00:00:00.000Z',
        },
        'Preset 2': {
          name: 'Preset 2',
          config: { project_name: 'project-2' },
          createdAt: '2023-01-02T00:00:00.000Z',
        },
      }

      localStorage.setItem(CUSTOM_PRESETS_KEY, JSON.stringify(oldData))

      const presets = loadCustomPresets()
      expect(Object.keys(presets)).toHaveLength(2)
      expect(presets['Preset 1'].name).toBe('Preset 1')
      expect(presets['Preset 2'].name).toBe('Preset 2')
    })
  })

  // ========================================
  // Integration Tests
  // ========================================
  describe('Integration Tests', () => {
    it('should save, load, and delete preset', () => {
      const config: Partial<RisoConfig> = {
        project_name: 'integration-test',
        api_module: 'enabled',
      }

      saveCustomPreset('Integration', config, 'Integration test preset')

      let presets = loadCustomPresets()
      expect(presets['Integration']).toBeDefined()

      deleteCustomPreset('Integration')

      presets = loadCustomPresets()
      expect(presets['Integration']).toBeUndefined()
    })

    it('should export, import, and share preset', () => {
      const original: CustomPreset = {
        name: 'Full Workflow',
        description: 'Full workflow test',
        config: {
          project_name: 'full-workflow',
          api_module: 'enabled',
          api_languages: ['python'],
        },
        createdAt: '2024-01-01T00:00:00.000Z',
        version: 1,
      }

      // Export
      const yaml = exportPresetYAML(original)

      // Import
      const imported = importPresetYAML(yaml)

      // Share
      const url = generateShareableURL(imported.config)

      // Parse shared URL
      const parsed = parseShareableURL(url)

      expect(parsed).toEqual(imported.config)
    })

    it('should handle full preset lifecycle', () => {
      const config: Partial<RisoConfig> = {
        project_name: 'lifecycle-test',
        project_layout: 'monorepo',
        api_module: 'enabled',
      }

      // Create
      saveCustomPreset('Lifecycle', config, 'Lifecycle test')

      // Load
      let presets = loadCustomPresets()
      expect(presets['Lifecycle']).toBeDefined()

      // Export
      const exported = exportPresetYAML(presets['Lifecycle'])
      expect(exported).toContain('project_name: lifecycle-test')

      // Share
      const url = generateShareableURL(config)
      expect(url).toContain('preset=')

      // Delete
      deleteCustomPreset('Lifecycle')
      presets = loadCustomPresets()
      expect(presets['Lifecycle']).toBeUndefined()
    })

    it('should handle multiple presets independently', () => {
      const config1: Partial<RisoConfig> = {
        project_name: 'independent-1',
      }
      const config2: Partial<RisoConfig> = {
        project_name: 'independent-2',
      }

      saveCustomPreset('Preset A', config1)
      saveCustomPreset('Preset B', config2)

      const url1 = generateShareableURL(config1)
      const url2 = generateShareableURL(config2)

      const parsed1 = parseShareableURL(url1)
      const parsed2 = parseShareableURL(url2)

      expect(parsed1).not.toEqual(parsed2)
      expect(parsed1?.project_name).toBe('independent-1')
      expect(parsed2?.project_name).toBe('independent-2')
    })
  })
})
