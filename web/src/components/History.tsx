import { useState } from 'react'
import { useRisoStore, type ConfigHistory } from '../lib/store'
import { History as HistoryIcon, Trash2, Upload, ChevronDown, ChevronUp } from 'lucide-react'
import { cn } from '../lib/utils'

export function History() {
  const { history, loadFromHistory, deleteFromHistory, setStep } = useRisoStore()
  const [isOpen, setIsOpen] = useState(false)

  if (history.length === 0) {
    return null
  }

  const handleLoad = (id: string) => {
    loadFromHistory(id)
    setStep(5) // Go to review step
    setIsOpen(false)
  }

  return (
    <div className="mb-6">
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-controls="riso-history-list"
        className="flex items-center gap-2 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
      >
        <HistoryIcon className="h-4 w-4" />
        Saved Configurations ({history.length})
        {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {isOpen && (
        <div id="riso-history-list" className="mt-3 space-y-2">
          {history.map((item) => (
            <HistoryItem
              key={item.id}
              item={item}
              onLoad={() => handleLoad(item.id)}
              onDelete={() => deleteFromHistory(item.id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function HistoryItem({
  item,
  onLoad,
  onDelete,
}: {
  item: ConfigHistory
  onLoad: () => void
  onDelete: () => void
}) {
  const config = item.config
  const summary = [
    config.project_layout,
    config.api_tracks !== 'none' ? `API: ${config.api_tracks}` : null,
    config.docs_site !== 'none' ? config.docs_site : null,
    config.saas_starter_module === 'enabled' ? 'SaaS' : null,
  ].filter(Boolean).join(' • ')

  const timestamp = new Date(item.timestamp).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <div className={cn(
      'flex items-center justify-between p-4 rounded-2xl border',
      'bg-white/80 dark:bg-gray-900/70 border-white/70 dark:border-gray-700/60'
    )}>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900 dark:text-white truncate">
            {item.name}
          </span>
          <span className="text-xs text-gray-400">{timestamp}</span>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
          {summary || 'Default configuration'}
        </p>
      </div>

      <div className="flex items-center gap-1 ml-2">
        <button
          onClick={onLoad}
          aria-label={`Load ${item.name}`}
          className="p-2 text-riso-600 dark:text-riso-400 hover:bg-riso-50 dark:hover:bg-riso-900/20 rounded-md transition-colors"
          title="Load configuration"
        >
          <Upload className="h-4 w-4" />
        </button>
        <button
          onClick={onDelete}
          aria-label={`Delete ${item.name}`}
          className="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
          title="Delete configuration"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
