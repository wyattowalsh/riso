import type { RisoConfig } from './store'
import { stringify, parse } from 'yaml'
import {
  applyThenRejectRemovedKeys,
  formatRemapPreview,
} from './removedAnswerKeys'
import {
  parseCustomPresetsStorage,
  parseShareConfigPayload,
} from './configSchemas'

const CUSTOM_PRESETS_KEY = 'riso-custom-presets'

const PRESET_META_KEYS = new Set([
  'name',
  'description',
  'version',
  'createdAt',
  'config',
])

export interface CustomPreset {
  name: string
  description?: string
  config: Partial<RisoConfig>
  createdAt: string
  version: number
  remapPreview?: string[]
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function omitPresetMeta(parsed: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {}
  for (const [key, value] of Object.entries(parsed)) {
    if (!PRESET_META_KEYS.has(key)) {
      out[key] = value
    }
  }
  return out
}

/**
 * Save a custom preset to localStorage
 */
export function saveCustomPreset(
  name: string,
  config: Partial<RisoConfig>,
  description?: string
): void {
  const presets = loadCustomPresets()
  const preset: CustomPreset = {
    name,
    description,
    config,
    createdAt: new Date().toISOString(),
    version: 1,
  }
  presets[name] = preset
  localStorage.setItem(CUSTOM_PRESETS_KEY, JSON.stringify(presets))
}

/**
 * Load all custom presets from localStorage
 */
export function loadCustomPresets(): Record<string, CustomPreset> {
  try {
    const stored = localStorage.getItem(CUSTOM_PRESETS_KEY)
    if (!stored) {
      return {}
    }
    const parsed = JSON.parse(stored) as unknown
    const validated = parseCustomPresetsStorage(parsed)
    return validated as Record<string, CustomPreset>
  } catch (error) {
    console.error('Failed to load custom presets:', error)
    return {}
  }
}

/**
 * Delete a custom preset
 */
export function deleteCustomPreset(name: string): boolean {
  const presets = loadCustomPresets()
  if (presets[name]) {
    delete presets[name]
    localStorage.setItem(CUSTOM_PRESETS_KEY, JSON.stringify(presets))
    return true
  }
  return false
}

/**
 * Export preset to YAML string
 */
export function exportPresetYAML(preset: CustomPreset): string {
  const remapped = applyThenRejectRemovedKeys({
    ...(preset.config as Record<string, unknown>),
  })
  return stringify({
    name: preset.name,
    description: preset.description,
    version: preset.version,
    config: remapped.answers,
  })
}

/**
 * Import preset from YAML string
 */
export function importPresetYAML(yamlStr: string): CustomPreset {
  const parsed = parse(yamlStr)
  if (!isRecord(parsed)) {
    throw new Error('Invalid configuration format')
  }
  const configBlock = parsed.config
  const hasConfigBlock = isRecord(configBlock)
  const source = hasConfigBlock ? { ...configBlock } : omitPresetMeta(parsed)
  const remapped = applyThenRejectRemovedKeys(source)
  if (hasConfigBlock) {
    applyThenRejectRemovedKeys(omitPresetMeta(parsed))
  }
  const projectName = remapped.answers.project_name
  const name =
    typeof parsed.name === 'string' && parsed.name.trim()
      ? parsed.name
      : !hasConfigBlock && typeof projectName === 'string' && projectName.trim()
        ? projectName
        : 'Imported Preset'
  const description =
    typeof parsed.description === 'string' ? parsed.description : undefined
  const version = typeof parsed.version === 'number' ? parsed.version : 1

  return {
    name,
    description,
    config: remapped.answers as CustomPreset['config'],
    createdAt: new Date().toISOString(),
    version,
    remapPreview: formatRemapPreview(remapped.ops),
  }
}

/**
 * Generate shareable URL with encoded config
 */
export function generateShareableURL(config: Partial<RisoConfig>): string {
  const remapped = applyThenRejectRemovedKeys({
    ...(config as Record<string, unknown>),
  })
  const compressed = btoa(JSON.stringify(remapped.answers))
  return `${window.location.origin}${window.location.pathname}?preset=${encodeURIComponent(compressed)}`
}

/**
 * Parse shareable URL to config
 */
export function parseShareableURL(url: string): Partial<RisoConfig> | null {
  let urlObj: URL
  try {
    urlObj = new URL(url)
  } catch {
    return null
  }
  const preset = urlObj.searchParams.get('preset')
  if (!preset) return null
  let raw: unknown
  try {
    raw = JSON.parse(atob(decodeURIComponent(preset)))
  } catch {
    return null
  }
  const parsed = parseShareConfigPayload(raw)
  if (!parsed.success) {
    throw new Error(parsed.error)
  }
  return parsed.data as Partial<RisoConfig>
}
