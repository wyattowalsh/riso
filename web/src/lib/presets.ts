import type { RisoConfig } from './store'
import { stringify, parse } from 'yaml'
import { formatRemovedAnswerKeyErrors } from './removedAnswerKeys'

const CUSTOM_PRESETS_KEY = 'riso-custom-presets'

export interface CustomPreset {
  name: string
  description?: string
  config: Partial<RisoConfig>
  createdAt: string
  version: number
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
    return stored ? JSON.parse(stored) : {}
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
  return stringify({
    name: preset.name,
    description: preset.description,
    version: preset.version,
    config: preset.config,
  })
}

/**
 * Import preset from YAML string
 */
export function importPresetYAML(yamlStr: string): CustomPreset {
  const parsed = parse(yamlStr) as Record<string, unknown>
  const removedKeyErrors = formatRemovedAnswerKeyErrors(parsed)
  if (removedKeyErrors.length > 0) {
    throw new Error(
      `Removed Copier answer keys are no longer supported:\n${removedKeyErrors.map((line) => `- ${line}`).join('\n')}`,
    )
  }
  const config = (parsed.config ?? parsed) as Record<string, unknown>
  const configErrors = formatRemovedAnswerKeyErrors(config)
  if (configErrors.length > 0) {
    throw new Error(
      `Removed Copier answer keys are no longer supported:\n${configErrors.map((line) => `- ${line}`).join('\n')}`,
    )
  }
  const name = typeof parsed.name === 'string' ? parsed.name : 'Imported Preset'
  const description =
    typeof parsed.description === 'string' ? parsed.description : undefined
  const version = typeof parsed.version === 'number' ? parsed.version : 1
  const configSource = parsed.config ?? parsed

  return {
    name,
    description,
    config: configSource as CustomPreset['config'],
    createdAt: new Date().toISOString(),
    version,
  }
}

/**
 * Generate shareable URL with encoded config
 */
export function generateShareableURL(config: Partial<RisoConfig>): string {
  const compressed = btoa(JSON.stringify(config))
  return `${window.location.origin}${window.location.pathname}?preset=${encodeURIComponent(compressed)}`
}

/**
 * Parse shareable URL to config
 */
export function parseShareableURL(url: string): Partial<RisoConfig> | null {
  try {
    const urlObj = new URL(url)
    const preset = urlObj.searchParams.get('preset')
    if (!preset) return null
    return JSON.parse(atob(decodeURIComponent(preset)))
  } catch {
    return null
  }
}
