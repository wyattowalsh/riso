import { useMemo, useState } from 'react'
import { Check, LinkIcon, X } from 'lucide-react'
import { copyToClipboard } from '../../lib/utils'
import { generateShareableURL } from '../../lib/presets'
import type { RisoConfig } from '../../lib/store'

/**
 * Props for the SharePresetModal component
 */
interface SharePresetModalProps {
  /** The preset configuration to share */
  presetConfig: Partial<RisoConfig> | null
  /** Callback when the modal should close */
  onClose: () => void
}

/**
 * Modal dialog for sharing a preset configuration via URL
 * Generates a shareable URL and provides copy functionality
 */
export function SharePresetModal({ presetConfig, onClose }: SharePresetModalProps) {
  const [copied, setCopied] = useState(false)
  const shareUrl = useMemo(
    () => (presetConfig ? generateShareableURL(presetConfig) : ''),
    [presetConfig]
  )

  if (!presetConfig) return null

  const handleCopy = async () => {
    await copyToClipboard(shareUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 max-w-lg w-full shadow-xl border border-gray-200 dark:border-gray-800">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Share Preset
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Shareable URL
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={shareUrl}
                readOnly
                className="input-riso flex-1 font-mono text-xs"
              />
              <button
                onClick={handleCopy}
                className="btn-primary px-4 flex items-center gap-2"
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4" />
                    Copied
                  </>
                ) : (
                  <>
                    <LinkIcon className="h-4 w-4" />
                    Copy
                  </>
                )}
              </button>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Share this URL to let others use your preset configuration.
            </p>
          </div>

          <div className="flex justify-end pt-2">
            <button onClick={onClose} className="btn-ghost">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
