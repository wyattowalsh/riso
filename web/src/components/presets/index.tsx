import { useState, useCallback } from 'react'
import { useRisoStore } from '../../lib/store'
import { copyToClipboard } from '../../lib/utils'
import {
  saveCustomPreset,
  loadCustomPresets,
  generateShareableURL,
  type CustomPreset
} from '../../lib/presets'
import { PresetsGrid } from './PresetsGrid'
import { CustomPresetsSection } from './CustomPresetsSection'
import { SavePresetModal } from './SavePresetModal'
import type { Preset } from './types'
import type { RisoConfig } from '../../lib/store'

/**
 * Main Presets component that orchestrates preset selection and management
 * Provides both built-in quick-start presets and custom preset functionality
 */
export function Presets() {
  const { config, resetConfig, updateConfig, setStep } = useRisoStore()
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null)
  const [celebratingPreset, setCelebratingPreset] = useState<string | null>(null)
  const [customPresets, setCustomPresets] = useState<Record<string, CustomPreset>>(
    () => loadCustomPresets()
  )
  const [showSaveModal, setShowSaveModal] = useState(false)

  const applyPreset = useCallback((preset: Preset, _event: React.MouseEvent) => {
    // Reset config first to clear any existing selections, then apply preset
    resetConfig()
    updateConfig(preset.config)

    // Navigate to review after a brief delay for the animation
    setTimeout(() => {
      setStep(5) // Jump to review step
      setCelebratingPreset(null)
    }, 400)
  }, [resetConfig, updateConfig, setStep])

  const applyCustomPreset = useCallback((preset: CustomPreset, _event: React.MouseEvent) => {
    // Reset config first to clear any existing selections, then apply preset
    resetConfig()
    updateConfig(preset.config)

    // Navigate to review after a brief delay for the animation
    setTimeout(() => {
      setStep(5) // Jump to review step
      setCelebratingPreset(null)
    }, 400)
  }, [resetConfig, updateConfig, setStep])

  const handleSavePreset = useCallback((name: string, description: string) => {
    saveCustomPreset(name, config, description)
    setCustomPresets(loadCustomPresets())
    setShowSaveModal(false)
  }, [config])

  const handleSharePreset = useCallback(async (presetConfig: Partial<RisoConfig>) => {
    const url = generateShareableURL(presetConfig)
    await copyToClipboard(url)
  }, [])

  return (
    <div className="space-y-8">
      {/* Built-in Presets */}
      <PresetsGrid
        selectedPreset={selectedPreset}
        celebratingPreset={celebratingPreset}
        onApplyPreset={applyPreset}
        setSelectedPreset={setSelectedPreset}
        setCelebratingPreset={setCelebratingPreset}
      />

      {/* Custom Presets Section */}
      <CustomPresetsSection
        customPresets={customPresets}
        setCustomPresets={setCustomPresets}
        selectedPreset={selectedPreset}
        celebratingPreset={celebratingPreset}
        setSelectedPreset={setSelectedPreset}
        setCelebratingPreset={setCelebratingPreset}
        onOpenSaveModal={() => setShowSaveModal(true)}
        onSharePreset={handleSharePreset}
        onApplyCustomPreset={applyCustomPreset}
      />

      {/* Save Modal */}
      <SavePresetModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        onSave={handleSavePreset}
      />
    </div>
  )
}

// Re-export all components for external use
export { PresetsGrid } from './PresetsGrid'
export { CustomPresetsSection } from './CustomPresetsSection'
export { SavePresetModal } from './SavePresetModal'
export { SharePresetModal } from './SharePresetModal'
export { PresetCard } from './PresetCard'
export { CustomPresetCard } from './CustomPresetCard'
export { createConfetti } from './ConfettiEffect'
export { PRESETS } from './presets'
export type { Preset } from './types'
