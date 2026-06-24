import { Check, Download, Trash2, LinkIcon, Sparkles } from 'lucide-react'
import { cn } from '../../lib/utils'
import type { CustomPreset } from '../../lib/presets'
import type { RisoConfig } from '../../lib/store'

/**
 * Props for the CustomPresetCard component
 */
interface CustomPresetCardProps {
  /** The custom preset to display */
  preset: CustomPreset
  /** Whether this preset is currently selected */
  isSelected: boolean
  /** Whether this preset is celebrating (confetti animation) */
  isCelebrating: boolean
  /** Whether delete confirmation is showing */
  showDeleteConfirm: boolean
  /** Whether the share link was copied */
  copied: boolean
  /** Click handler for applying the preset */
  onClick: (preset: CustomPreset, event: React.MouseEvent) => void
  /** Click handler for sharing the preset */
  onShare: (config: Partial<RisoConfig>) => void
  /** Click handler for exporting the preset */
  onExport: (preset: CustomPreset) => void
  /** Click handler for showing delete confirmation */
  onShowDeleteConfirm: () => void
  /** Click handler for hiding delete confirmation */
  onHideDeleteConfirm: () => void
  /** Click handler for confirming deletion */
  onConfirmDelete: () => void
}

/**
 * A card component for displaying a single custom preset
 * Includes action buttons for share, export, and delete
 */
export function CustomPresetCard({
  preset,
  isSelected,
  isCelebrating,
  showDeleteConfirm,
  copied,
  onClick,
  onShare,
  onExport,
  onShowDeleteConfirm,
  onHideDeleteConfirm,
  onConfirmDelete,
}: CustomPresetCardProps) {
  return (
    <div
      className={cn(
        'preset-card riso-card-gradient p-5 rounded-2xl',
        'group relative',
        'border-2 border-riso-orange/30 dark:border-riso-apricot/30',
        isCelebrating && 'animate-celebrate',
        isSelected && 'ring-2 ring-riso-orange/50 dark:ring-riso-apricot/50'
      )}
    >
      {/* Selection checkmark */}
      {isSelected && (
        <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-riso-green flex items-center justify-center animate-bounce-in shadow-lg">
          <Check className="h-4 w-4 text-white" />
        </div>
      )}

      <button
        onClick={(e) => onClick(preset, e)}
        className="text-left w-full mb-3"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-riso-orange/20 to-riso-apricot/20 transition-transform duration-300 group-hover:scale-110">
            <Sparkles className="h-6 w-6 text-riso-orange dark:text-riso-apricot" />
          </div>
          <div className="font-medium text-gray-900 dark:text-white text-sm group-hover:text-riso-orange dark:group-hover:text-riso-apricot transition-colors">
            {preset.name}
          </div>
        </div>
        {preset.description && (
          <p className="text-xs text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors">
            {preset.description}
          </p>
        )}
        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
          Created: {new Date(preset.createdAt).toLocaleDateString()}
        </p>
      </button>

      {/* Action buttons */}
      <div className="flex gap-2 mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={() => onShare(preset.config)}
          className="flex-1 btn-ghost text-xs py-1.5 flex items-center justify-center gap-1"
          title="Copy share link"
        >
          {copied ? <Check className="h-3 w-3" /> : <LinkIcon className="h-3 w-3" />}
          <span className="sr-only">Copy share link</span>
        </button>
        <button
          onClick={() => onExport(preset)}
          className="flex-1 btn-ghost text-xs py-1.5 flex items-center justify-center gap-1"
          title="Export preset"
        >
          <Download className="h-3 w-3" />
          <span className="sr-only">Export</span>
        </button>
        <button
          onClick={onShowDeleteConfirm}
          className="flex-1 btn-ghost text-xs py-1.5 flex items-center justify-center gap-1 text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-900/20"
          title="Delete preset"
        >
          <Trash2 className="h-3 w-3" />
          <span className="sr-only">Delete</span>
        </button>
      </div>

      {/* Delete confirmation */}
      {showDeleteConfirm && (
        <div className="absolute inset-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm rounded-2xl flex items-center justify-center p-4 z-10">
          <div className="text-center space-y-3">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              Delete this preset?
            </p>
            <div className="flex gap-2">
              <button
                onClick={onConfirmDelete}
                className="btn-primary text-xs bg-red-600 hover:bg-red-700"
              >
                Delete
              </button>
              <button
                onClick={onHideDeleteConfirm}
                className="btn-ghost text-xs"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Hover shine effect */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 pointer-events-none" />
    </div>
  )
}
