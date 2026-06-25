/**
 * SearchBox Component
 *
 * Command palette-style search across all configuration options.
 * Press Cmd/Ctrl+K to open, type to search, arrow keys to navigate.
 */

import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { Search, X, ArrowRight, Command } from 'lucide-react'
import { useDebounce } from 'use-debounce'
import { cn } from '../lib/utils'
import { useRisoStore } from '../lib/store'
import {
  buildSearchIndex,
  searchOptions,
  STEP_NAMES,
  SUGGESTED_SEARCHES,
  type SearchResult,
} from '../lib/search'

interface SearchBoxProps {
  onNavigateToStep?: (step: number, field?: string) => void
}

export function SearchBox({ onNavigateToStep }: SearchBoxProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)
  const { setCurrentStep, setHighlightedField } = useRisoStore()

  // Build search index once
  const searchIndex = useMemo(() => buildSearchIndex(), [])

  // Debounce the search query (300ms delay)
  const [debouncedQuery] = useDebounce(query, 300)

  // Search results using debounced query
  const results = useMemo(() => {
    if (!debouncedQuery || debouncedQuery.length < 2) return []
    return searchOptions(debouncedQuery, searchIndex)
  }, [debouncedQuery, searchIndex])

  const closeSearch = useCallback(() => {
    setIsOpen(false)
    setQuery('')
    setSelectedIndex(0)
  }, [])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl+K to open
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsOpen(true)
      }
      // Escape to close
      if (e.key === 'Escape' && isOpen) {
        e.preventDefault()
        closeSearch()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, closeSearch])

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Handle result selection
  const handleSelectResult = useCallback(
    (result: SearchResult) => {
      const { step, key } = result.option
      if (step >= 0) {
        // Set the highlighted field and navigate to step
        setHighlightedField(key)
        setCurrentStep(step)
        onNavigateToStep?.(step, key)

        // Clear highlight after 3 seconds
        setTimeout(() => {
          setHighlightedField(null)
        }, 3000)
      }
      closeSearch()
    },
    [setHighlightedField, setCurrentStep, onNavigateToStep, closeSearch]
  )

  // Keyboard navigation within results
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.max(prev - 1, 0))
      } else if (e.key === 'Enter' && results[selectedIndex]) {
        e.preventDefault()
        handleSelectResult(results[selectedIndex])
      }
    },
    [results, selectedIndex, handleSelectResult]
  )

  // Handle suggested search click
  const handleSuggestedSearch = (searchQuery: string) => {
    setQuery(searchQuery)
    inputRef.current?.focus()
  }

  // Scroll selected item into view
  useEffect(() => {
    if (resultsRef.current && results.length > 0) {
      const selectedElement = resultsRef.current.children[selectedIndex] as HTMLElement
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest' })
      }
    }
  }, [selectedIndex, results.length])

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-800/50 text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600 transition-colors text-sm"
      >
        <Search className="h-4 w-4" />
        <span>Search options...</span>
        <kbd className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-xs text-gray-500 dark:text-gray-400 font-mono">
          <Command className="h-3 w-3" />K
        </kbd>
      </button>
    )
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
        onClick={closeSearch}
      />

      {/* Modal */}
      <div className="fixed inset-x-4 top-[10%] z-50 mx-auto max-w-xl">
        <div className="overflow-hidden rounded-2xl bg-white dark:bg-gray-900 shadow-2xl ring-1 ring-gray-200 dark:ring-gray-800">
          {/* Search input */}
          <div className="flex items-center border-b border-gray-200 dark:border-gray-800 px-4">
            <Search className="h-5 w-5 text-gray-400" />
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
              className="flex-1 bg-transparent px-3 py-4 text-gray-900 dark:text-white placeholder-gray-400 outline-none"
            />
            {query && (
              <button
                onClick={() => setQuery('')}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <X className="h-4 w-4 text-gray-400" />
              </button>
            )}
            <button
              onClick={closeSearch}
              className="ml-2 px-2 py-1 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
            >
              esc
            </button>
          </div>

          {/* Results or suggestions */}
          <div className="max-h-80 overflow-y-auto p-2" ref={resultsRef}>
            {results.length > 0 ? (
              results.map((result, index) => (
                <ResultItem
                  key={result.option.key}
                  result={result}
                  isSelected={index === selectedIndex}
                  onClick={() => handleSelectResult(result)}
                  onMouseEnter={() => setSelectedIndex(index)}
                />
              ))
            ) : query.length >= 2 ? (
              <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                No results for "{query}"
              </div>
            ) : (
              <div className="space-y-3 p-2">
                <div className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider px-2">
                  Suggested searches
                </div>
                <div className="grid gap-1">
                  {SUGGESTED_SEARCHES.map((suggestion) => (
                    <button
                      key={suggestion.query}
                      onClick={() => handleSuggestedSearch(suggestion.query)}
                      className="flex items-center justify-between px-3 py-2 rounded-lg text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                      <span className="text-gray-700 dark:text-gray-300">{suggestion.query}</span>
                      <span className="text-xs text-gray-400">{suggestion.description}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between border-t border-gray-200 dark:border-gray-800 px-4 py-2 text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 font-mono">↑↓</kbd>
                navigate
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 font-mono">↵</kbd>
                select
              </span>
            </div>
            <span>{searchIndex.length} options</span>
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
  const { option } = result

  return (
    <button
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      className={cn(
        'w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-colors',
        isSelected
          ? 'bg-riso-orange/10 text-riso-orange dark:bg-riso-orange/20'
          : 'hover:bg-gray-100 dark:hover:bg-gray-800'
      )}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              'font-medium truncate',
              isSelected ? 'text-riso-orange' : 'text-gray-900 dark:text-white'
            )}
          >
            {option.label}
          </span>
          <span className="flex-shrink-0 px-1.5 py-0.5 rounded text-xs bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400">
            {option.category}
          </span>
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
          {option.description}
        </div>
      </div>
      <div className="flex items-center gap-2 flex-shrink-0 ml-3">
        <span className="text-xs text-gray-400">
          {option.step >= 0 ? STEP_NAMES[option.step] : 'Global'}
        </span>
        <ArrowRight
          className={cn(
            'h-4 w-4',
            isSelected ? 'text-riso-orange' : 'text-gray-300 dark:text-gray-600'
          )}
        />
      </div>
    </button>
  )
}

// Compact trigger button for use in header
export function SearchTrigger({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="p-2 rounded-lg text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100 hover:bg-white/80 dark:hover:bg-gray-900/80 transition-colors"
      aria-label="Search options (Cmd+K)"
    >
      <Search className="h-5 w-5" />
    </button>
  )
}
