import { Check, Sparkles, Info } from 'lucide-react'
import { cn } from '../../lib/utils'
import { PRESET_ACCENTS, ICON_GRADIENTS, ICON_TEXT, type Preset } from './types'

/**
 * Props for the PresetCard component
 */
interface PresetCardProps {
  /** The preset configuration to display */
  preset: Preset
  /** Index for staggered animation */
  index: number
  /** Whether this preset is currently selected */
  isSelected: boolean
  /** Whether this preset is celebrating (confetti animation) */
  isCelebrating: boolean
  /** Click handler for applying the preset */
  onClick: (preset: Preset, event: React.MouseEvent) => void
  /** Click handler for showing preset details */
  onShowDetails?: (preset: Preset) => void
  /** Use compact styling for bento grid secondary cards */
  compact?: boolean
}

/**
 * A reusable card component for displaying a single preset
 * Includes animations, selection states, and hover effects
 */
export function PresetCard({
  preset,
  index,
  isSelected,
  isCelebrating,
  onClick,
  onShowDetails,
  compact = false,
}: PresetCardProps) {
  return (
    <div
      className={cn(
        'preset-card riso-card-gradient riso-card-accent text-left',
        'group relative',
        'animate-scale-in stagger-item',
        PRESET_ACCENTS[preset.id],
        isCelebrating && 'animate-celebrate',
        isSelected && 'ring-2 ring-riso-federal-blue/50 dark:ring-riso-cornflower/50',
        compact ? 'p-3 rounded-xl' : 'p-5 rounded-2xl'
      )}
      style={{ animationDelay: `${index * 50}ms`, opacity: 1 }}
      data-selected={isSelected}
    >
      {/* Selection checkmark */}
      {isSelected && (
        <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-riso-green flex items-center justify-center animate-bounce-in shadow-lg z-10">
          <Check className="h-4 w-4 text-white" />
        </div>
      )}

      {/* Info button */}
      {onShowDetails && !compact && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onShowDetails(preset)
          }}
          className="absolute top-2 right-2 p-1.5 rounded-lg bg-white/80 dark:bg-gray-800/80 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white dark:hover:bg-gray-800 z-10"
          aria-label={`View details for ${preset.name}`}
        >
          <Info className="h-4 w-4 text-gray-500 dark:text-gray-400" />
        </button>
      )}

      <button
        onClick={(e) => onClick(preset, e)}
        className="w-full text-left"
      >
        <div className={cn('flex items-center gap-3', compact ? 'mb-1.5' : 'mb-2')}>
          <div className={cn(
            'rounded-xl bg-gradient-to-br transition-transform duration-300 group-hover:scale-110',
            ICON_GRADIENTS[preset.id],
            compact ? 'p-2' : 'p-2.5'
          )}>
            <div className={cn(ICON_TEXT[preset.id], 'transition-transform duration-300')}>
              {preset.icon}
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <div className={cn(
              'font-medium text-gray-900 dark:text-white group-hover:text-riso-federal-blue dark:group-hover:text-riso-cornflower transition-colors',
              compact ? 'text-xs' : 'text-sm'
            )}>
              {preset.name}
            </div>
            {!compact && (
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className={cn(
                  'px-1.5 py-0.5 rounded text-[9px] font-medium',
                  preset.complexity === 'beginner' && 'bg-riso-green/20 text-riso-green',
                  preset.complexity === 'intermediate' && 'bg-riso-sunflower/20 text-riso-orange',
                  preset.complexity === 'advanced' && 'bg-riso-fluorescent-pink/20 text-riso-fluorescent-pink'
                )}>
                  {preset.complexity}
                </span>
                <span className="text-[9px] text-gray-400">~{preset.estimatedFiles} files</span>
              </div>
            )}
          </div>
        </div>
        <p className={cn(
          'text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors',
          compact ? 'text-[10px] leading-tight' : 'text-xs'
        )}>
          {preset.description}
        </p>
      </button>

      {/* Hover shine effect */}
      <div className={cn(
        'absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 pointer-events-none',
        compact ? 'rounded-xl' : 'rounded-2xl'
      )} />
    </div>
  )
}

/**
 * Props for the FeaturedPresetCard component
 */
interface FeaturedPresetCardProps {
  /** The preset configuration to display */
  preset: Preset
  /** Whether this preset is currently selected */
  isSelected: boolean
  /** Whether this preset is celebrating (confetti animation) */
  isCelebrating: boolean
  /** Click handler for applying the preset */
  onClick: (preset: Preset, event: React.MouseEvent) => void
  /** Click handler for showing preset details */
  onShowDetails?: (preset: Preset) => void
}

/**
 * A large featured card for the bento grid hero position
 * Includes recommended badge and feature highlights
 */
export function FeaturedPresetCard({
  preset,
  isSelected,
  isCelebrating,
  onClick,
  onShowDetails,
}: FeaturedPresetCardProps) {
  return (
    <div
      className={cn(
        'preset-card riso-card-gradient riso-card-accent p-6 rounded-2xl text-left h-full w-full',
        'group relative flex flex-col',
        'animate-scale-in',
        PRESET_ACCENTS[preset.id],
        isCelebrating && 'animate-celebrate',
        isSelected && 'ring-2 ring-riso-federal-blue/50 dark:ring-riso-cornflower/50'
      )}
      data-selected={isSelected}
    >
      {/* Recommended badge */}
      <div className="absolute -top-2 -left-2 px-2 py-1 bg-riso-sunflower text-riso-ink-black text-[10px] font-bold uppercase tracking-wider rounded-full shadow-lg flex items-center gap-1 z-10">
        <Sparkles className="h-3 w-3" />
        Recommended
      </div>

      {isSelected && (
        <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-riso-green flex items-center justify-center animate-bounce-in shadow-lg z-10">
          <Check className="h-4 w-4 text-white" />
        </div>
      )}

      {/* Info button */}
      {onShowDetails && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onShowDetails(preset)
          }}
          className="absolute top-2 right-2 p-1.5 rounded-lg bg-white/80 dark:bg-gray-800/80 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white dark:hover:bg-gray-800 z-10"
          aria-label={`View details for ${preset.name}`}
        >
          <Info className="h-4 w-4 text-gray-500 dark:text-gray-400" />
        </button>
      )}

      <button
        onClick={(e) => onClick(preset, e)}
        className="flex-1 flex flex-col text-left w-full"
      >
        <div className="flex items-center gap-3 mb-3">
          <div className={cn(
            'p-3 rounded-xl bg-gradient-to-br transition-transform duration-300 group-hover:scale-110',
            ICON_GRADIENTS[preset.id]
          )}>
            <div className={cn(ICON_TEXT[preset.id], 'transition-transform duration-300')}>
              {preset.icon}
            </div>
          </div>
          <div>
            <div className="font-semibold text-lg text-gray-900 dark:text-white group-hover:text-riso-federal-blue dark:group-hover:text-riso-cornflower transition-colors">
              {preset.name}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Full-Stack Template
            </div>
          </div>
        </div>

        <p className="text-sm text-gray-600 dark:text-gray-300 group-hover:text-gray-700 dark:group-hover:text-gray-200 transition-colors flex-grow">
          {preset.description}
        </p>

        {/* Feature highlights */}
        <div className="mt-4 flex flex-wrap gap-1.5">
          {['Monorepo', 'GraphQL', 'MCP', 'Fumadocs'].map(tag => (
            <span key={tag} className="px-2 py-0.5 bg-white/50 dark:bg-gray-800/50 rounded text-[10px] font-medium text-gray-600 dark:text-gray-400">
              {tag}
            </span>
          ))}
        </div>
      </button>

      {/* Hover shine effect */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 pointer-events-none" />
    </div>
  )
}
