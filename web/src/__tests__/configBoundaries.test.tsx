import { beforeEach, describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { render, screen } from '@testing-library/react'
import { parse, stringify } from 'yaml'
import App from '../App'
import {
  parseShareConfigPayload,
  parseCustomPresetsStorage,
} from '../lib/configSchemas'
import { configToCopierArgs, generateYamlConfig } from '../lib/exportConfig'
import { importPresetYAML, saveCustomPreset } from '../lib/presets'
import {
  defaultRisoConfig,
  mergePersistedWizardState,
  useRisoStore,
} from '../lib/store'
import type { RisoConfig } from '../lib/store'
import { getPrompt } from '../lib/matrixData'
import { api } from '../lib/api'

beforeEach(() => {
  window.history.replaceState({}, '', '/')
  localStorage.setItem('riso-dark-mode', 'false')
  useRisoStore.getState().resetConfig()
  useRisoStore.setState({ history: [] })
})

describe('public Copier answer round trips', () => {
  it('validates against metadata that matches the current Copier prompt contract', () => {
    const copier = parse(
      readFileSync(
        join(
          dirname(fileURLToPath(import.meta.url)),
          '../../../template/copier.yml',
        ),
        'utf8',
      ),
    ) as Record<string, Record<string, unknown>>
    for (const [key, definition] of Object.entries(copier)) {
      if (
        key.startsWith('_') ||
        !definition ||
        typeof definition !== 'object' ||
        !definition.type
      )
        continue
      const metadata = getPrompt(key)
      expect(metadata, `Missing generated metadata for ${key}`).toBeDefined()
      expect(metadata?.type, key).toBe(definition.type)
      expect(metadata?.choices, key).toEqual(definition.choices ?? null)
      expect(metadata?.multiselect ?? false, key).toBe(
        definition.multiselect ?? false,
      )
    }
  })
  it.each([
    {
      desktop_module: 'enabled',
      desktop_framework: 'tauri',
      desktop_features: 'tray_icon',
      desktop_platforms: 'linux',
    },
    {
      mcp_module: 'enabled',
      mcp_languages: ['go'],
      mcp_transport: 'http',
      mcp_example_tools: false,
      go_version: '1.24',
      python_versions: ['3.13'],
    },
    {
      saas_infra_module: 'enabled',
      saas_multi_tenancy_level: 'enterprise',
      saas_tenancy_model: 'b2b-teams',
      saas_rbac_system: 'custom-permissions',
      saas_waitlist: true,
      saas_gdpr_tools: true,
      saas_ai_features: 'rag',
      vector_db_provider: 'qdrant',
      embedding_provider: 'cohere',
    },
    {
      api_module: 'enabled',
      api_languages: ['go'],
      go_framework: 'echo',
      include_databases: 'yes',
      project_slug: 'custom-slug',
      package_name: 'custom_package',
    },
  ])('retains imported settings through YAML download: %j', (settings) => {
    const original = { project_name: 'round-trip', ...settings }
    const imported = importPresetYAML(stringify(original))
    const downloaded = parse(generateYamlConfig(imported.config))
    expect(downloaded).toEqual(original)
  })

  it('normalizes valid Copier API feature lists without losing selections', () => {
    const imported = importPresetYAML('api_features: [graphql, websocket]')
    expect(imported.config.api_features).toBe('graphql,websocket')
    expect(configToCopierArgs(imported.config).api_features).toEqual([
      'graphql',
      'websocket',
    ])
  })

  it('preserves explicit empty language selections for generation validation', () => {
    expect(
      configToCopierArgs({ api_module: 'enabled', api_languages: [] }),
    ).toMatchObject({ api_languages: [] })
  })

  it('ignores Copier source metadata rather than treating it as user options', () => {
    const imported = importPresetYAML(
      '_src_path: /a/template\n_commit: v2\nproject_name: copied-app',
    )
    expect(configToCopierArgs(imported.config)).toEqual({
      project_name: 'copied-app',
    })
  })
})

describe('untrusted configuration boundaries', () => {
  it.each([
    { project_name: 42 },
    { api_languages: 'python' },
    { api_languages: [false] },
    { mcp_languages: ['javascript'] },
    { api_features: ['graphql', 'shell'] },
    { saas_waitlist: 'yes' },
    { desktop_framework: 'unsupported' },
    { arbitrary_option: true },
  ])('rejects malformed YAML/share data: %j', (config) => {
    expect(parseShareConfigPayload(config).success).toBe(false)
    expect(() => importPresetYAML(stringify(config))).toThrow()
    expect(() => api.importConfig(stringify(config))).toThrow()
  })

  it('rejects malformed config envelopes', () => {
    expect(() =>
      importPresetYAML('name: wrong-shape\nconfig: [python]'),
    ).toThrow(/mapping/)
  })

  it('validates before updating or replacing existing state', () => {
    useRisoStore.getState().updateConfig({ project_name: 'existing-project' })
    const original = useRisoStore.getState().config
    const invalid = { project_name: 42 } as unknown as Partial<RisoConfig>
    expect(() => useRisoStore.getState().updateConfig(invalid)).toThrow(
      /project_name/,
    )
    expect(() => useRisoStore.getState().replaceConfig(invalid)).toThrow(
      /project_name/,
    )
    expect(useRisoStore.getState().config).toBe(original)
  })

  it('does not persist malformed custom presets and keeps valid stored entries', () => {
    expect(() =>
      saveCustomPreset('bad', {
        saas_waitlist: 'yes',
      } as unknown as Partial<RisoConfig>),
    ).toThrow()
    expect(localStorage.getItem('riso-custom-presets')).toBeNull()
    const parsed = parseCustomPresetsStorage({
      good: { config: { project_name: 'good-project' } },
      bad: { config: { project_name: 42 } },
      badArray: { config: ['python'] },
    })
    expect(Object.keys(parsed)).toEqual(['good'])
  })

  it('rejects corrupt persisted config/history without crashing hydration', () => {
    const result = mergePersistedWizardState(
      {
        config: { project_name: 42 },
        history: [
          {
            id: 'good',
            name: 'good',
            config: { project_name: 'valid-history' },
            timestamp: '2026-01-01',
          },
          {
            id: 'bad',
            name: 'bad',
            config: { api_languages: 'python' },
            timestamp: '2026-01-01',
          },
          null,
        ],
        currentStep: 500,
      },
      useRisoStore.getState(),
    )
    expect(result.config.project_name).toBe('')
    expect(result.currentStep).toBe(0)
    expect(result.history.map((item) => item.id)).toEqual(['good'])
  })

  it('ignores malformed history containers', () => {
    expect(
      mergePersistedWizardState({ history: {} }, useRisoStore.getState())
        .history,
    ).toEqual([])
  })
})

describe('shared configurations', () => {
  it('replaces prior SaaS choices when opening a CLI-only share', () => {
    useRisoStore.getState().updateConfig({
      project_name: 'old-saas',
      saas_infra_module: 'enabled',
      saas_auth_module: 'enabled',
      saas_billing_module: 'enabled',
    })
    const payload = {
      project_name: 'shared-cli',
      cli_module: 'enabled',
      cli_languages: ['python'],
    }
    window.history.replaceState(
      {},
      '',
      `/?preset=${encodeURIComponent(btoa(JSON.stringify(payload)))}`,
    )
    render(<App />)
    const config = useRisoStore.getState().config
    expect(config.project_name).toBe('shared-cli')
    expect(config.cli_module).toBe('enabled')
    expect(config.saas_infra_module).toBe(defaultRisoConfig.saas_infra_module)
    expect(config.saas_billing_module).toBe(
      defaultRisoConfig.saas_billing_module,
    )
  })

  it('never lets persisted config overwrite an externally supplied share', () => {
    const result = mergePersistedWizardState(
      { config: { project_name: 'old-saas', saas_infra_module: 'enabled' } },
      useRisoStore.getState(),
      {
        href: `https://riso.test/?preset=${btoa(JSON.stringify({ project_name: 'shared-project' }))}`,
      },
    )
    expect(result.config.project_name).toBe('')
    expect(result.config.saas_infra_module).toBe('disabled')
  })

  it('preserves valid persisted state when a share payload is rejected', () => {
    const result = mergePersistedWizardState(
      {
        config: { project_name: 'saved-project', saas_infra_module: 'enabled' },
      },
      useRisoStore.getState(),
      {
        href: `https://riso.test/?preset=${btoa(JSON.stringify({ project_name: 42 }))}`,
      },
    )
    expect(result.config.project_name).toBe('saved-project')
    expect(result.config.saas_infra_module).toBe('enabled')
  })

  it('reports malformed shares while preserving existing valid state', () => {
    useRisoStore.getState().updateConfig({ project_name: 'existing-project' })
    window.history.replaceState(
      {},
      '',
      `/?preset=${encodeURIComponent(btoa(JSON.stringify({ project_name: 42 })))}`,
    )
    render(<App />)
    expect(screen.getByRole('alert')).toHaveTextContent(/project_name/)
    expect(useRisoStore.getState().config.project_name).toBe('existing-project')
  })
})
