/**
 * SearchModal Component
 *
 * Global command palette for searching configuration options.
 * Opens with Cmd+K (Mac) / Ctrl+K (Windows/Linux).
 *
 * Features:
 * - Fuzzy search across 140+ config options
 * - Keyboard navigation (arrow keys, Enter, Escape)
 * - Auto-navigate to correct wizard step on selection
 * - Recent searches persisted in localStorage
 * - Results grouped by category with icons
 */

import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import {
  Search,
  X,
  ArrowRight,
  Command,
  Clock,
  Settings,
  Terminal,
  Server,
  FileText,
  Sparkles,
  Database,
  Shield,
  CreditCard,
  Layers,
  Bot,
  Wrench,
  GitBranch,
} from 'lucide-react'
import { useDebounce } from 'use-debounce'
import { cn } from '../lib/utils'
import { useRisoStore } from '../lib/store'
import {
  buildSearchIndex,
  searchOptions,
  STEP_NAMES,
  SUGGESTED_SEARCHES,
  type SearchResult,
  type SearchableOption,
} from '../lib/search'
import { searchDocs, type DocSearchResult } from '../lib/docSearch'
import { ExternalLink, BookOpen } from 'lucide-react'

// localStorage key for recent searches
const RECENT_SEARCHES_KEY = 'riso-recent-searches'
const MAX_RECENT_SEARCHES = 5

function loadRecentSearches(): RecentSearch[] {
  try {
    const stored = localStorage.getItem(RECENT_SEARCHES_KEY)
    if (stored) {
      return (JSON.parse(stored) as RecentSearch[]).slice(0, MAX_RECENT_SEARCHES)
    }
  } catch {
    // Ignore parse errors
  }
  return []
}

// Category icons mapping
const CATEGORY_ICONS: Record<string, React.ElementType> = {
  Project: Settings,
  CLI: Terminal,
  API: Server,
  MCP: Bot,
  Documentation: FileText,
  Fumadocs: FileText,
  Docusaurus: FileText,
  SaaS: Layers,
  'AI Tools': Sparkles,
  'CI/CD': GitBranch,
  Quality: Shield,
  Codegen: Wrench,
  Changelog: FileText,
  'Shared Logic': Database,
  Infrastructure: Database,
  Auth: Shield,
  Billing: CreditCard,
  Other: Settings,
}

interface RecentSearch {
  key: string
  label: string
  category: string
  step: number
  timestamp: number
}

interface SearchModalProps {
  isOpen: boolean
  onClose: () => void
  onNavigateToStep?: (step: number, field?: string) => void
}

export function SearchModal({ isOpen, onClose, onNavigateToStep }: SearchModalProps) {
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>(loadRecentSearches)
  const [docResults, setDocResults] = useState<DocSearchResult[]>([])
  const inputRef = useRef<HTMLInputElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)
  const { setCurrentStep, setHighlightedField } = useRisoStore()

  // Build search index once
  const searchIndex = useMemo(() => buildSearchIndex(), [])

  // Debounce the search query (150ms delay for snappier feel)
  const [debouncedQuery] = useDebounce(query, 150)

  // Search results using debounced query
  const results = useMemo(() => {
    if (!debouncedQuery || debouncedQuery.length < 2) return []
    return searchOptions(debouncedQuery, searchIndex)
  }, [debouncedQuery, searchIndex])

  // Group results by category
  const groupedResults = useMemo(() => {
    const groups: Record<string, SearchResult[]> = {}
    for (const result of results) {
      const category = result.option.category
      if (!groups[category]) {
        groups[category] = []
      }
      groups[category].push(result)
    }
    return groups
  }, [results])

  // Flatten grouped results for keyboard navigation
  const flatResults = useMemo(() => {
    const flat: SearchResult[] = []
    for (const category of Object.keys(groupedResults)) {
      flat.push(...groupedResults[category])
    }
    return flat
  }, [groupedResults])

  const docSearchQuery =
    debouncedQuery && debouncedQuery.length >= 2 ? debouncedQuery : null

  // Search documentation when query changes
  useEffect(() => {
    if (!docSearchQuery) return

    let cancelled = false
    searchDocs(docSearchQuery).then((results) => {
      if (!cancelled) setDocResults(results)
    })
    return () => {
      cancelled = true
    }
  }, [docSearchQuery])

  const displayedDocResults = docSearchQuery ? docResults : []

  // Save recent search to localStorage
  const saveRecentSearch = useCallback((option: SearchableOption) => {
    const newRecent: RecentSearch = {
      key: option.key,
      label: option.label,
      category: option.category,
      step: option.step,
      timestamp: Date.now(),
    }

    setRecentSearches((prev) => {
      // Remove duplicate if exists
      const filtered = prev.filter((r) => r.key !== option.key)
      // Add new at front, limit to max
      const updated = [newRecent, ...filtered].slice(0, MAX_RECENT_SEARCHES)
      // Save to localStorage
      try {
        localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated))
      } catch {
        // Ignore storage errors
      }
      return updated
    })
  }, [])

  // Clear recent searches
  const clearRecentSearches = useCallback(() => {
    setRecentSearches([])
    try {
      localStorage.removeItem(RECENT_SEARCHES_KEY)
    } catch {
      // Ignore storage errors
    }
  }, [])

  const handleClose = useCallback(() => {
    setQuery('')
    setSelectedIndex(0)
    onClose()
  }, [onClose])

  // Keyboard shortcuts for closing
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        handleClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, handleClose])

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      // Small delay to ensure modal is rendered
      const timer = setTimeout(() => {
        inputRef.current?.focus()
      }, 50)
      return () => clearTimeout(timer)
    }
  }, [isOpen])

  // Handle result selection
  const handleSelectResult = useCallback(
    (result: SearchResult) => {
      const { step, key } = result.option
      if (step >= 0) {
        // Save to recent searches
        saveRecentSearch(result.option)

        // Set the highlighted field and navigate to step
        setHighlightedField(key)
        setCurrentStep(step)
        onNavigateToStep?.(step, key)

        // Scroll to wizard
        setTimeout(() => {
          document.getElementById('wizard')?.scrollIntoView({ behavior: 'smooth' })
        }, 100)

        // Clear highlight after 3 seconds
        setTimeout(() => {
          setHighlightedField(null)
        }, 3000)
      }
      handleClose()
    },
    [saveRecentSearch, setHighlightedField, setCurrentStep, onNavigateToStep, handleClose]
  )

  // Handle recent search click
  const handleRecentClick = useCallback(
    (recent: RecentSearch) => {
      if (recent.step >= 0) {
        // Update timestamp
        saveRecentSearch({
          key: recent.key,
          label: recent.label,
          category: recent.category,
          step: recent.step,
          description: '',
          keywords: [],
        } as SearchableOption)

        setHighlightedField(recent.key)
        setCurrentStep(recent.step)
        onNavigateToStep?.(recent.step, recent.key)

        setTimeout(() => {
          document.getElementById('wizard')?.scrollIntoView({ behavior: 'smooth' })
        }, 100)

        setTimeout(() => {
          setHighlightedField(null)
        }, 3000)
      }
      handleClose()
    },
    [saveRecentSearch, setHighlightedField, setCurrentStep, onNavigateToStep, handleClose]
  )

  // Keyboard navigation within results
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const itemCount = flatResults.length > 0 ? flatResults.length : recentSearches.length
      if (itemCount === 0) return

      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.min(prev + 1, itemCount - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.max(prev - 1, 0))
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (flatResults.length > 0 && flatResults[selectedIndex]) {
          handleSelectResult(flatResults[selectedIndex])
        } else if (recentSearches.length > 0 && recentSearches[selectedIndex]) {
          handleRecentClick(recentSearches[selectedIndex])
        }
      }
    },
    [flatResults, recentSearches, selectedIndex, handleSelectResult, handleRecentClick]
  )

  // Handle suggested search click
  const handleSuggestedSearch = (searchQuery: string) => {
    setQuery(searchQuery)
    setSelectedIndex(0)
    inputRef.current?.focus()
  }

  // Scroll selected item into view
  useEffect(() => {
    if (resultsRef.current) {
      const selectedElement = resultsRef.current.querySelector('[data-selected="true"]')
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest' })
      }
    }
  }, [selectedIndex])

  if (!isOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm transition-opacity duration-300"
        onClick={handleClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        className="fixed inset-x-4 top-[8%] z-50 mx-auto max-w-2xl animate-scale-in"
        role="dialog"
        aria-modal="true"
        aria-label="Search configuration options"
      >
        <div className="overflow-hidden rounded-2xl bg-white dark:bg-gray-900 shadow-2xl ring-1 ring-gray-200/50 dark:ring-gray-700/50">
          {/* Search input header */}
          <div className="flex items-center gap-3 border-b border-gray-200 dark:border-gray-800 px-4 py-3">
            <Search className="h-5 w-5 text-gray-400 flex-shrink-0" aria-hidden="true" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value)
                setSelectedIndex(0)
              }}
              onKeyDown={handleKeyDown}
              placeholder="Search configuration options..."
              className="flex-1 bg-transparent text-base text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 outline-none font-sans"
              aria-label="Search input"
            />
            {query && (
              <button
                onClick={() => setQuery('')}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Clear search"
              >
                <X className="h-4 w-4 text-gray-400" />
              </button>
            )}
            <kbd className="hidden sm:flex items-center gap-0.5 px-2 py-1 rounded-md bg-gray-100 dark:bg-gray-800 text-xs text-gray-500 dark:text-gray-400 font-mono border border-gray-200 dark:border-gray-700">
              esc
            </kbd>
          </div>

          {/* Results or suggestions */}
          <div className="max-h-[60vh] overflow-y-auto" ref={resultsRef}>
            {(flatResults.length > 0 || displayedDocResults.length > 0) ? (
              /* Search results - config options and documentation */
              <div className="p-2">
                {/* Configuration options section */}
                {flatResults.length > 0 && (
                  <>
                    {Object.entries(groupedResults).map(([category, categoryResults]) => (
                      <div key={category} className="mb-3 last:mb-0">
                        {/* Category header */}
                        <div className="flex items-center gap-2 px-3 py-2">
                          {(() => {
                            const IconComponent = CATEGORY_ICONS[category] || Settings
                            return (
                              <IconComponent
                                className="h-4 w-4 text-gray-400 dark:text-gray-500"
                                aria-hidden="true"
                              />
                            )
                          })()}
                          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider font-sans">
                            {category}
                          </span>
                          <span className="text-xs text-gray-400 dark:text-gray-500">
                            ({categoryResults.length})
                          </span>
                        </div>
                        {/* Category results */}
                        <div className="space-y-0.5">
                          {categoryResults.map((result) => {
                            const globalIndex = flatResults.findIndex(
                              (r) => r.option.key === result.option.key
                            )
                            return (
                              <ResultItem
                                key={result.option.key}
                                result={result}
                                isSelected={globalIndex === selectedIndex}
                                onClick={() => handleSelectResult(result)}
                                onMouseEnter={() => setSelectedIndex(globalIndex)}
                              />
                            )
                          })}
                        </div>
                      </div>
                    ))}
                  </>
                )}

                {/* Documentation results section */}
                {displayedDocResults.length > 0 && (
                  <div className="mb-3 last:mb-0">
                    {/* Section header */}
                    <div className="flex items-center gap-2 px-3 py-2">
                      <BookOpen
                        className="h-4 w-4 text-gray-400 dark:text-gray-500"
                        aria-hidden="true"
                      />
                      <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider font-sans">
                        Documentation
                      </span>
                      <span className="text-xs text-gray-400 dark:text-gray-500">
                        ({displayedDocResults.length})
                      </span>
                    </div>
                    {/* Doc results list */}
                    <div className="space-y-0.5">
                      {displayedDocResults.map((doc) => (
                        <a
                          key={doc.url}
                          href={doc.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={cn(
                            'w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left transition-all duration-150',
                            'hover:bg-gray-100 dark:hover:bg-gray-800/70'
                          )}
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="font-medium truncate font-sans text-gray-900 dark:text-white">
                                {doc.title}
                              </span>
                              <span className="flex-shrink-0 px-1.5 py-0.5 rounded text-[10px] font-medium bg-riso-blue/10 text-riso-blue dark:bg-riso-blue/20">
                                docs
                              </span>
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5 font-sans">
                              {doc.docName.replace(/\//g, ' › ')}
                            </div>
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                            <ExternalLink className="h-4 w-4 text-gray-300 dark:text-gray-600" />
                          </div>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : query.length >= 2 ? (
              /* No results */
              <div className="p-8 text-center">
                <Search className="h-10 w-10 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400 font-sans">
                  No results for "<span className="font-medium">{query}</span>"
                </p>
                <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                  Try searching for "auth", "database", or "analytics"
                </p>
              </div>
            ) : (
              /* Initial state with recent searches and suggestions */
              <div className="p-3 space-y-4">
                {/* Recent searches */}
                {recentSearches.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between px-2 py-1">
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-gray-400" aria-hidden="true" />
                        <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider font-sans">
                          Recent
                        </span>
                      </div>
                      <button
                        onClick={clearRecentSearches}
                        className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                      >
                        Clear
                      </button>
                    </div>
                    <div className="mt-1 space-y-0.5">
                      {recentSearches.map((recent, index) => (
                        <button
                          key={recent.key}
                          onClick={() => handleRecentClick(recent)}
                          onMouseEnter={() => setSelectedIndex(index)}
                          data-selected={index === selectedIndex}
                          className={cn(
                            'w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left transition-all duration-150',
                            index === selectedIndex
                              ? 'bg-riso-federal-blue/10 dark:bg-riso-cornflower/20'
                              : 'hover:bg-gray-100 dark:hover:bg-gray-800/70'
                          )}
                        >
                          <div className="flex items-center gap-3 min-w-0">
                            {(() => {
                              const IconComponent = CATEGORY_ICONS[recent.category] || Settings
                              return (
                                <IconComponent
                                  className={cn(
                                    'h-4 w-4 flex-shrink-0',
                                    index === selectedIndex
                                      ? 'text-riso-federal-blue dark:text-riso-cornflower'
                                      : 'text-gray-400'
                                  )}
                                  aria-hidden="true"
                                />
                              )
                            })()}
                            <span
                              className={cn(
                                'font-medium truncate font-sans',
                                index === selectedIndex
                                  ? 'text-riso-federal-blue dark:text-riso-cornflower'
                                  : 'text-gray-700 dark:text-gray-300'
                              )}
                            >
                              {recent.label}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                            <span className="text-xs text-gray-400 dark:text-gray-500">
                              {recent.step >= 0 ? STEP_NAMES[recent.step] : 'Global'}
                            </span>
                            <ArrowRight
                              className={cn(
                                'h-4 w-4 transition-transform',
                                index === selectedIndex
                                  ? 'text-riso-federal-blue dark:text-riso-cornflower translate-x-0.5'
                                  : 'text-gray-300 dark:text-gray-600'
                              )}
                            />
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Suggested searches */}
                <div>
                  <div className="flex items-center gap-2 px-2 py-1">
                    <Sparkles className="h-4 w-4 text-gray-400" aria-hidden="true" />
                    <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider font-sans">
                      Suggestions
                    </span>
                  </div>
                  <div className="mt-1 grid grid-cols-2 gap-1.5">
                    {SUGGESTED_SEARCHES.map((suggestion) => (
                      <button
                        key={suggestion.query}
                        onClick={() => handleSuggestedSearch(suggestion.query)}
                        className="flex flex-col items-start px-3 py-2.5 rounded-xl text-left hover:bg-gray-100 dark:hover:bg-gray-800/70 transition-colors group"
                      >
                        <span className="font-medium text-sm text-gray-700 dark:text-gray-300 group-hover:text-riso-federal-blue dark:group-hover:text-riso-cornflower transition-colors font-sans">
                          {suggestion.query}
                        </span>
                        <span className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                          {suggestion.description}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer with keyboard hints */}
          <div className="flex items-center justify-between border-t border-gray-200 dark:border-gray-800 px-4 py-2.5 bg-gray-50/50 dark:bg-gray-800/30">
            <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1.5">
                <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-gray-800 font-mono border border-gray-200 dark:border-gray-700 shadow-sm">
                  <span className="text-[10px]">↑↓</span>
                </kbd>
                <span className="hidden sm:inline">navigate</span>
              </span>
              <span className="flex items-center gap-1.5">
                <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-gray-800 font-mono border border-gray-200 dark:border-gray-700 shadow-sm">
                  <span className="text-[10px]">↵</span>
                </kbd>
                <span className="hidden sm:inline">select</span>
              </span>
              <span className="flex items-center gap-1.5">
                <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-gray-800 font-mono border border-gray-200 dark:border-gray-700 shadow-sm">
                  <span className="text-[10px]">esc</span>
                </kbd>
                <span className="hidden sm:inline">close</span>
              </span>
            </div>
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {searchIndex.length} options
            </span>
          </div>
        </div>
      </div>
    </>
  )
}

interface ResultItemProps {
  result: SearchResult
  isSelected: boolean
  onClick: () => void
  onMouseEnter: () => void
}

function ResultItem({ result, isSelected, onClick, onMouseEnter }: ResultItemProps) {
  const { option, matches } = result

  return (
    <button
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      data-selected={isSelected}
      className={cn(
        'w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left transition-all duration-150',
        isSelected
          ? 'bg-riso-federal-blue/10 dark:bg-riso-cornflower/20'
          : 'hover:bg-gray-100 dark:hover:bg-gray-800/70'
      )}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              'font-medium truncate font-sans',
              isSelected
                ? 'text-riso-federal-blue dark:text-riso-cornflower'
                : 'text-gray-900 dark:text-white'
            )}
          >
            {option.label}
          </span>
          {/* Match indicators */}
          {matches.key && (
            <span className="flex-shrink-0 px-1.5 py-0.5 rounded text-[10px] font-medium bg-riso-green/10 text-riso-green dark:bg-riso-green/20">
              key
            </span>
          )}
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5 font-sans">
          {option.description}
        </div>
      </div>
      <div className="flex items-center gap-2 flex-shrink-0 ml-3">
        <span
          className={cn(
            'text-xs px-2 py-0.5 rounded-md',
            isSelected
              ? 'bg-riso-federal-blue/10 text-riso-federal-blue dark:bg-riso-cornflower/20 dark:text-riso-cornflower'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'
          )}
        >
          {option.step >= 0 ? STEP_NAMES[option.step] : 'Global'}
        </span>
        <ArrowRight
          className={cn(
            'h-4 w-4 transition-transform',
            isSelected
              ? 'text-riso-federal-blue dark:text-riso-cornflower translate-x-0.5'
              : 'text-gray-300 dark:text-gray-600'
          )}
        />
      </div>
    </button>
  )
}

// Hook for managing search modal state globally
export function useSearchModal() {
  const [isOpen, setIsOpen] = useState(false)

  // Global keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl+K to open
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsOpen(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
  }
}

// Trigger button component for header
interface SearchTriggerButtonProps {
  onClick: () => void
  className?: string
}

export function SearchTriggerButton({ onClick, className }: SearchTriggerButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'group relative flex items-center gap-2 px-3 py-1.5 rounded-xl',
        'border border-gray-200/80 dark:border-gray-700/60',
        'bg-white/70 dark:bg-gray-800/50',
        'hover:border-gray-300 dark:hover:border-gray-600',
        'hover:bg-white dark:hover:bg-gray-800',
        'transition-all duration-200',
        'text-gray-500 dark:text-gray-400',
        className
      )}
      aria-label="Search options (Cmd+K)"
    >
      <Search className="h-4 w-4" aria-hidden="true" />
      <span className="text-sm font-medium hidden lg:inline">Search...</span>
      <kbd className="hidden sm:flex items-center gap-0.5 px-1.5 py-0.5 rounded-md bg-gray-100 dark:bg-gray-700 text-xs text-gray-500 dark:text-gray-400 font-mono border border-gray-200/50 dark:border-gray-600/50">
        <Command className="h-3 w-3" aria-hidden="true" />
        <span>K</span>
      </kbd>
      {/* Tooltip on hover */}
      <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded-md bg-gray-900 dark:bg-gray-700 text-white text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
        Search all options
      </span>
    </button>
  )
}
