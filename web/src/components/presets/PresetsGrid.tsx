import { useCallback, useMemo, useState } from 'react'
import { ChevronUp, Sparkles, ArrowRight, Filter, X, Terminal, Rocket, Cpu } from 'lucide-react'
import { cn } from '../../lib/utils'
import { formatMatrixTimestamp, matrixMeta } from '../../lib/matrixData'
import { PresetCard, FeaturedPresetCard } from './PresetCard'
import { PresetDetailDrawer } from './PresetDetailDrawer'
import { createConfetti } from './ConfettiEffect'
import { PRESETS } from './presets'
import type { Preset, PresetTag } from './types'

/** Presets to show in bento grid initially (featured + 3 secondary) */
const FEATURED_INDEX = 6 // 'fullstack' preset
const SECONDARY_INDICES = [0, 1, 9] // minimal-python, python-api, saas-starter

/** Filter categories with display labels */
const TAG_CATEGORIES: { label: string; tags: PresetTag[] }[] = [
  { label: 'Language', tags: ['python', 'node', 'rust', 'go'] },
  { label: 'Type', tags: ['cli', 'api', 'saas', 'docs', 'mcp'] },
  { label: 'Layout', tags: ['monorepo', 'single-package'] },
  { label: 'Level', tags: ['beginner', 'intermediate', 'advanced'] },
]

/** Gallery categories for organized display */
const GALLERY_CATEGORIES = [
  { id: 'starter', label: 'Quick Start', icon: Sparkles, description: 'Get up and running fast', tags: ['beginner'] as PresetTag[] },
  { id: 'cli-api', label: 'CLI & APIs', icon: Terminal, description: 'Backend tools and services', tags: ['cli', 'api'] as PresetTag[] },
  { id: 'saas', label: 'SaaS & Full-Stack', icon: Rocket, description: 'Complete applications', tags: ['saas', 'fullstack'] as PresetTag[] },
  { id: 'advanced', label: 'Advanced', icon: Cpu, description: 'Complex architectures', tags: ['advanced', 'monorepo'] as PresetTag[] },
]

interface PresetsGridProps {
  selectedPreset: string | null
  celebratingPreset: string | null
  onApplyPreset: (preset: Preset, event: React.MouseEvent) => void
  setSelectedPreset: (id: string | null) => void
  setCelebratingPreset: (id: string | null) => void
}

export function PresetsGrid({
  selectedPreset,
  celebratingPreset,
  onApplyPreset,
  setSelectedPreset,
  setCelebratingPreset,
}: PresetsGridProps) {
  const [showAll, setShowAll] = useState(false)
  const [detailPreset, setDetailPreset] = useState<Preset | null>(null)
  const [activeTags, setActiveTags] = useState<Set<PresetTag>>(new Set())
  const [showFilters, setShowFilters] = useState(false)
  const matrixStamp = formatMatrixTimestamp(matrixMeta.generatedAt)

  const featuredPreset = PRESETS[FEATURED_INDEX]
  const secondaryPresets = SECONDARY_INDICES.map(i => PRESETS[i])
  const remainingCount = PRESETS.length - 4

  // Filter presets by active tags
  const filteredPresets = useMemo(() => {
    if (activeTags.size === 0) return PRESETS
    return PRESETS.filter(preset =>
      Array.from(activeTags).every(tag => preset.tags.includes(tag))
    )
  }, [activeTags])

  const toggleTag = useCallback((tag: PresetTag) => {
    setActiveTags(prev => {
      const next = new Set(prev)
      if (next.has(tag)) {
        next.delete(tag)
      } else {
        next.add(tag)
      }
      return next
    })
  }, [])

  const clearFilters = useCallback(() => {
    setActiveTags(new Set())
  }, [])

  const handleApplyPreset = useCallback((preset: Preset, event: React.MouseEvent) => {
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
    const x = rect.left + rect.width / 2
    const y = rect.top + rect.height / 2
    createConfetti(x, y)
    setCelebratingPreset(preset.id)
    setSelectedPreset(preset.id)
    onApplyPreset(preset, event)
    setTimeout(() => setCelebratingPreset(null), 400)
  }, [onApplyPreset, setSelectedPreset, setCelebratingPreset])

  const handleShowDetails = useCallback((preset: Preset) => {
    setDetailPreset(preset)
  }, [])

  const handleCloseDetails = useCallback(() => {
    setDetailPreset(null)
  }, [])

  const handleApplyFromDrawer = useCallback((preset: Preset) => {
    // Confetti from center of screen for drawer apply
    createConfetti(window.innerWidth / 2, window.innerHeight / 2)
    setCelebratingPreset(preset.id)
    setSelectedPreset(preset.id)
    onApplyPreset(preset, {} as React.MouseEvent)
    setTimeout(() => setCelebratingPreset(null), 400)
    setDetailPreset(null)
  }, [onApplyPreset, setSelectedPreset, setCelebratingPreset])

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="display-md text-gray-900 dark:text-white flex items-center gap-2">
            {showAll ? 'Template Gallery' : 'Quick Start Presets'}
            <Sparkles className="h-5 w-5 text-riso-sunflower" />
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {showAll
              ? 'Battle-tested configurations for Python, TypeScript, Rust & Go stacks.'
              : 'Production-ready stacks. One click to load, then customize.'
            }
          </p>
          {!showAll && (
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
              Based on matrix snapshot {matrixStamp ?? 'unknown'}
            </p>
          )}
        </div>

        {/* Filter toggle - only shown when expanded */}
        {showAll && (
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              showFilters || activeTags.size > 0
                ? 'bg-riso-federal-blue/10 text-riso-federal-blue dark:bg-riso-cornflower/10 dark:text-riso-cornflower'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
            )}
          >
            <Filter className="h-4 w-4" />
            Filter
            {activeTags.size > 0 && (
              <span className="ml-1 px-1.5 py-0.5 text-[10px] bg-riso-federal-blue dark:bg-riso-cornflower text-white rounded-full">
                {activeTags.size}
              </span>
            )}
          </button>
        )}
      </div>

      {/* Filter tags panel */}
      {showAll && showFilters && (
        <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl space-y-3 animate-fade-in">
          {TAG_CATEGORIES.map(category => (
            <div key={category.label} className="flex flex-wrap items-center gap-2">
              <span className="text-[10px] uppercase tracking-wider text-gray-500 dark:text-gray-400 font-semibold w-16 flex-shrink-0">
                {category.label}
              </span>
              {category.tags.map(tag => (
                <button
                  key={tag}
                  onClick={() => toggleTag(tag)}
                  className={cn(
                    'px-2 py-0.5 rounded text-xs font-medium transition-colors',
                    activeTags.has(tag)
                      ? 'bg-riso-federal-blue text-white dark:bg-riso-cornflower'
                      : 'bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                  )}
                >
                  {tag}
                </button>
              ))}
            </div>
          ))}
          {activeTags.size > 0 && (
            <div className="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {filteredPresets.length} preset{filteredPresets.length !== 1 ? 's' : ''} matching
              </span>
              <button
                onClick={clearFilters}
                className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
              >
                <X className="h-3 w-3" />
                Clear filters
              </button>
            </div>
          )}
        </div>
      )}

      {!showAll ? (
        /* Bento Grid Layout */
        <div className="bento-grid">
          {/* Featured Card - Large */}
          <div className="bento-featured">
            <FeaturedPresetCard
              preset={featuredPreset}
              isSelected={selectedPreset === featuredPreset.id}
              isCelebrating={celebratingPreset === featuredPreset.id}
              onClick={handleApplyPreset}
              onShowDetails={handleShowDetails}
            />
          </div>

          {/* Secondary Cards - Stacked */}
          <div className="bento-secondary">
            {secondaryPresets.map((preset, index) => (
              <PresetCard
                key={preset.id}
                preset={preset}
                index={index}
                isSelected={selectedPreset === preset.id}
                isCelebrating={celebratingPreset === preset.id}
                onClick={handleApplyPreset}
                onShowDetails={handleShowDetails}
                compact
              />
            ))}

            {/* Expand Button */}
            <button
              onClick={() => setShowAll(true)}
              className="bento-expand-btn group"
            >
              <span className="font-medium">Explore {remainingCount} more</span>
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </button>
          </div>
        </div>
      ) : (
        /* Expanded Gallery View */
        <>
          {filteredPresets.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500 dark:text-gray-400">No presets match your filters.</p>
              <button
                onClick={clearFilters}
                className="mt-2 text-sm text-riso-federal-blue dark:text-riso-cornflower hover:underline"
              >
                Clear filters
              </button>
            </div>
          ) : activeTags.size > 0 ? (
            /* Flat grid when filtering */
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {filteredPresets.map((preset, index) => (
                <PresetCard
                  key={preset.id}
                  preset={preset}
                  index={index}
                  isSelected={selectedPreset === preset.id}
                  isCelebrating={celebratingPreset === preset.id}
                  onClick={handleApplyPreset}
                  onShowDetails={handleShowDetails}
                />
              ))}
            </div>
          ) : (
            /* Categorized gallery view */
            <div className="space-y-8">
              {GALLERY_CATEGORIES.map((category, catIndex) => {
                const categoryPresets = PRESETS.filter(preset =>
                  category.tags.some(tag => preset.tags.includes(tag))
                )
                if (categoryPresets.length === 0) return null

                const Icon = category.icon
                return (
                  <div key={category.id} className="space-y-3">
                    {/* Category Header */}
                    <div className="flex items-center gap-3 pb-2 border-b border-gray-100 dark:border-gray-800">
                      <div className={cn(
                        'p-2 rounded-lg',
                        catIndex === 0 && 'bg-riso-green/10',
                        catIndex === 1 && 'bg-riso-federal-blue/10',
                        catIndex === 2 && 'bg-riso-sunflower/10',
                        catIndex === 3 && 'bg-riso-grape/10'
                      )}>
                        <Icon className={cn(
                          'h-4 w-4',
                          catIndex === 0 && 'text-riso-green',
                          catIndex === 1 && 'text-riso-federal-blue dark:text-riso-cornflower',
                          catIndex === 2 && 'text-riso-sunflower',
                          catIndex === 3 && 'text-riso-grape'
                        )} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white text-sm">
                          {category.label}
                        </h4>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {category.description}
                        </p>
                      </div>
                      <span className="ml-auto text-xs text-gray-400 dark:text-gray-500 tabular-nums">
                        {categoryPresets.length} preset{categoryPresets.length !== 1 ? 's' : ''}
                      </span>
                    </div>

                    {/* Category Presets */}
                    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                      {categoryPresets.map((preset, index) => (
                        <PresetCard
                          key={preset.id}
                          preset={preset}
                          index={catIndex * 10 + index}
                          isSelected={selectedPreset === preset.id}
                          isCelebrating={celebratingPreset === preset.id}
                          onClick={handleApplyPreset}
                          onShowDetails={handleShowDetails}
                        />
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          <button
            onClick={() => setShowAll(false)}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors"
          >
            <ChevronUp className="h-4 w-4" />
            Show fewer presets
          </button>
        </>
      )}

      {/* Preset Detail Drawer */}
      <PresetDetailDrawer
        preset={detailPreset}
        isOpen={detailPreset !== null}
        onClose={handleCloseDetails}
        onApply={handleApplyFromDrawer}
        isSelected={detailPreset?.id === selectedPreset}
      />
    </div>
  )
}
