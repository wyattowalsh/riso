import { useCallback, useState } from 'react'
import { Plus, Upload } from 'lucide-react'
import { downloadFile } from '../../lib/utils'
import {
  deleteCustomPreset,
  exportPresetYAML,
  importPresetYAML,
  saveCustomPreset,
  loadCustomPresets,
  type CustomPreset
} from '../../lib/presets'
import { createConfetti } from './ConfettiEffect'
import { CustomPresetCard } from './CustomPresetCard'
import type { RisoConfig } from '../../lib/store'

/**
 * Props for the CustomPresetsSection component
 */
interface CustomPresetsSectionProps {
  /** Map of custom presets */
  customPresets: Record<string, CustomPreset>
  /** Updates the custom presets */
  setCustomPresets: (presets: Record<string, CustomPreset>) => void
  /** Currently selected preset ID */
  selectedPreset: string | null
  /** Preset currently showing celebration animation */
  celebratingPreset: string | null
  /** Updates the selected preset ID */
  setSelectedPreset: (id: string | null) => void
  /** Updates the celebrating preset ID */
  setCelebratingPreset: (id: string | null) => void
  /** Opens the save preset modal */
  onOpenSaveModal: () => void
  /** Callback when sharing a preset */
  onSharePreset: (config: Partial<RisoConfig>) => void
  /** Callback when applying a custom preset */
  onApplyCustomPreset: (preset: CustomPreset, event: React.MouseEvent) => void
}

/**
 * Section for managing custom presets
 * Includes saving, loading, exporting, importing, and deleting custom configurations
 */
export function CustomPresetsSection({
  customPresets,
  setCustomPresets,
  selectedPreset,
  celebratingPreset,
  setSelectedPreset,
  setCelebratingPreset,
  onOpenSaveModal,
  onSharePreset,
  onApplyCustomPreset,
}: CustomPresetsSectionProps) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const handleApplyCustomPreset = useCallback((preset: CustomPreset, event: React.MouseEvent) => {
    // Get click coordinates for confetti
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
    const x = rect.left + rect.width / 2
    const y = rect.top + rect.height / 2

    // Trigger confetti
    createConfetti(x, y)

    // Set celebration state
    setCelebratingPreset(`custom-${preset.name}`)
    setSelectedPreset(`custom-${preset.name}`)

    // Delegate to parent handler
    onApplyCustomPreset(preset, event)

    // Clear celebration after animation
    setTimeout(() => {
      setCelebratingPreset(null)
    }, 400)
  }, [onApplyCustomPreset, setSelectedPreset, setCelebratingPreset])

  const handleDeletePreset = useCallback((name: string) => {
    deleteCustomPreset(name)
    setCustomPresets(loadCustomPresets())
    setShowDeleteConfirm(null)
  }, [setCustomPresets])

  const handleExportPreset = useCallback((preset: CustomPreset) => {
    const yamlContent = exportPresetYAML(preset)
    downloadFile(yamlContent, `${preset.name}.preset.yml`, 'text/yaml')
  }, [])

  const handleImportPreset = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string
        const imported = importPresetYAML(content)
        saveCustomPreset(imported.name, imported.config, imported.description)
        setCustomPresets(loadCustomPresets())
      } catch (error) {
        console.error('Failed to import preset:', error)
        alert('Failed to import preset. Please check the file format.')
      }
    }
    reader.readAsText(file)
  }, [setCustomPresets])

  const handleSharePreset = useCallback((config: Partial<RisoConfig>) => {
    onSharePreset(config)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }, [onSharePreset])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="display-md text-gray-900 dark:text-white">Custom Presets</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Save and manage your own preset configurations.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={onOpenSaveModal}
            className="btn-primary text-sm flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Save Current
          </button>
          <label className="btn-secondary text-sm flex items-center gap-2 cursor-pointer">
            <Upload className="h-4 w-4" />
            Import
            <input
              type="file"
              accept=".yml,.yaml"
              onChange={handleImportPreset}
              className="sr-only"
            />
          </label>
        </div>
      </div>

      {Object.keys(customPresets).length === 0 ? (
        <div className="p-8 text-center border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-2xl">
          <p className="text-gray-500 dark:text-gray-400">
            No custom presets yet. Save your current configuration to get started.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Object.values(customPresets).map((preset) => (
            <CustomPresetCard
              key={preset.name}
              preset={preset}
              isSelected={selectedPreset === `custom-${preset.name}`}
              isCelebrating={celebratingPreset === `custom-${preset.name}`}
              showDeleteConfirm={showDeleteConfirm === preset.name}
              copied={copied}
              onClick={handleApplyCustomPreset}
              onShare={handleSharePreset}
              onExport={handleExportPreset}
              onShowDeleteConfirm={() => setShowDeleteConfirm(preset.name)}
              onHideDeleteConfirm={() => setShowDeleteConfirm(null)}
              onConfirmDelete={() => handleDeletePreset(preset.name)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
