import { useState } from 'react'
import { X } from 'lucide-react'

/**
 * Props for the SavePresetModal component
 */
interface SavePresetModalProps {
  /** Whether the modal is visible */
  isOpen: boolean
  /** Callback when the modal should close */
  onClose: () => void
  /** Callback when a preset should be saved */
  onSave: (name: string, description: string) => void
}

/**
 * Modal dialog for saving the current configuration as a custom preset
 * Includes form for preset name and optional description
 */
export function SavePresetModal({ isOpen, onClose, onSave }: SavePresetModalProps) {
  const [presetName, setPresetName] = useState('')
  const [presetDescription, setPresetDescription] = useState('')

  if (!isOpen) return null

  const handleSave = () => {
    if (!presetName.trim()) return
    onSave(presetName.trim(), presetDescription.trim())
    setPresetName('')
    setPresetDescription('')
  }

  const handleClose = () => {
    setPresetName('')
    setPresetDescription('')
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 max-w-md w-full shadow-xl border border-gray-200 dark:border-gray-800">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Save Custom Preset
          </h3>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Preset Name
            </label>
            <input
              type="text"
              value={presetName}
              onChange={(e) => setPresetName(e.target.value)}
              placeholder="My Custom Preset"
              className="input-riso w-full"
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description (optional)
            </label>
            <textarea
              value={presetDescription}
              onChange={(e) => setPresetDescription(e.target.value)}
              placeholder="Brief description of this preset..."
              rows={3}
              className="input-riso w-full resize-none"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              onClick={handleSave}
              disabled={!presetName.trim()}
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Save Preset
            </button>
            <button
              onClick={handleClose}
              className="btn-ghost flex-1"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
