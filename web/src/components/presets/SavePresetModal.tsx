import { useState, useRef, useCallback } from 'react'
import { useFocusTrap } from '../../lib/useFocusTrap'
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
  const dialogRef = useRef<HTMLDivElement>(null)

  const handleClose = useCallback(() => {
    setPresetName('')
    setPresetDescription('')
    onClose()
  }, [onClose])

  useFocusTrap(isOpen, dialogRef, handleClose)

  if (!isOpen) return null

  const handleSave = () => {
    if (!presetName.trim()) return
    onSave(presetName.trim(), presetDescription.trim())
    setPresetName('')
    setPresetDescription('')
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      role="presentation"
      onClick={handleClose}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="save-preset-title"
        className="bg-white dark:bg-gray-900 rounded-2xl p-6 max-w-md w-full shadow-xl border border-gray-200 dark:border-gray-800"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h3
            id="save-preset-title"
            className="text-lg font-semibold text-gray-900 dark:text-white"
          >
            Save Custom Preset
          </h3>
          <button
            type="button"
            onClick={handleClose}
            aria-label="Close save preset dialog"
            className="rounded-lg p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-riso-federal-blue"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label
              htmlFor="save-preset-name"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Preset Name
            </label>
            <input
              id="save-preset-name"
              type="text"
              value={presetName}
              onChange={(e) => setPresetName(e.target.value)}
              placeholder="My Custom Preset"
              className="input-riso w-full"
              autoFocus
            />
          </div>

          <div>
            <label
              htmlFor="save-preset-description"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Description (optional)
            </label>
            <textarea
              id="save-preset-description"
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
