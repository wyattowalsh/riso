/**
 * MCP Connection Status Indicator
 *
 * Shows connection state and provides connect/disconnect controls.
 */

import { useMCP } from '../lib/useMCP'
import { Wifi, WifiOff, Loader2 } from 'lucide-react'
import { cn } from '../lib/utils'

interface MCPStatusProps {
  /** Show as compact badge */
  compact?: boolean
  /** Additional class names */
  className?: string
}

export function MCPStatus({ compact = false, className }: MCPStatusProps) {
  const { connected, connecting, error, connect, disconnect } = useMCP()

  if (compact) {
    return (
      <button
        onClick={connected ? disconnect : connect}
        disabled={connecting}
        className={cn(
          'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium transition-colors',
          connected
            ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
            : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700',
          className
        )}
        aria-label={
          connecting
            ? 'Connecting to MCP server...'
            : connected
              ? 'MCP server connected. Click to disconnect.'
              : 'MCP server offline. Click to connect.'
        }
      >
        {connecting ? (
          <Loader2 className="h-3 w-3 animate-spin" aria-hidden="true" />
        ) : connected ? (
          <Wifi className="h-3 w-3" aria-hidden="true" />
        ) : (
          <WifiOff className="h-3 w-3" aria-hidden="true" />
        )}
        <span className="sr-only sm:not-sr-only">
          {connecting ? 'Connecting...' : connected ? 'MCP' : 'Offline'}
        </span>
      </button>
    )
  }

  return (
    <div className={cn('riso-card-soft p-4', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-xl',
              connected
                ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400'
                : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
            )}
            aria-hidden="true"
          >
            {connecting ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : connected ? (
              <Wifi className="h-5 w-5" />
            ) : (
              <WifiOff className="h-5 w-5" />
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              MCP Server
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {connecting
                ? 'Connecting...'
                : connected
                  ? 'Connected to riso-mcp'
                  : error ?? 'Not connected'}
            </p>
          </div>
        </div>

        <button
          onClick={connected ? disconnect : connect}
          disabled={connecting}
          aria-busy={connecting}
          className={cn(
            'rounded-lg px-4 py-2 text-sm font-medium transition-colors',
            connected
              ? 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700'
              : 'bg-riso-500 text-white hover:bg-riso-600 disabled:opacity-50'
          )}
        >
          {connecting ? 'Connecting...' : connected ? 'Disconnect' : 'Connect'}
        </button>
      </div>

      {error && !connected && (
        <p className="mt-3 text-xs text-amber-600 dark:text-amber-400">
          💡 Start the MCP server: <code className="bg-gray-100 dark:bg-gray-800 px-1 rounded">uv run riso-mcp --transport sse</code>
        </p>
      )}
    </div>
  )
}
