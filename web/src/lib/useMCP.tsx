/**
 * React hooks and context for MCP integration
 */

import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react'
import { getMCPClient, type MCPClientConfig, type RisoMCPClient } from './mcp-client'

interface MCPContextValue {
  client: RisoMCPClient
  connected: boolean
  connecting: boolean
  error: string | null
  connect: () => Promise<void>
  disconnect: () => Promise<void>
}

const MCPContext = createContext<MCPContextValue | null>(null)

interface MCPProviderProps {
  children: ReactNode
  config?: MCPClientConfig
  /** Auto-connect on mount (default: false) */
  autoConnect?: boolean
}

/**
 * Provider component for MCP client access
 */
export function MCPProvider({ children, config, autoConnect = false }: MCPProviderProps) {
  const [client] = useState(() => getMCPClient(config))
  const [connected, setConnected] = useState(false)
  const [connecting, setConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const connect = useCallback(async () => {
    if (connected || connecting) return
    
    setConnecting(true)
    setError(null)
    
    try {
      await client.connect()
      setConnected(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed')
      setConnected(false)
    } finally {
      setConnecting(false)
    }
  }, [client, connected, connecting])

  const disconnect = useCallback(async () => {
    try {
      await client.disconnect()
    } finally {
      setConnected(false)
    }
  }, [client])

  useEffect(() => {
    if (autoConnect) {
      connect()
    }
    
    return () => {
      // Disconnect but don't reset the singleton - other components may still use it
      client.disconnect().catch(() => {
        // Ignore disconnect errors on cleanup
      })
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <MCPContext.Provider value={{ client, connected, connecting, error, connect, disconnect }}>
      {children}
    </MCPContext.Provider>
  )
}

/**
 * Hook to access MCP client and connection state
 */
export function useMCP() {
  const context = useContext(MCPContext)
  if (!context) {
    throw new Error('useMCP must be used within an MCPProvider')
  }
  return context
}

/**
 * Hook for calling MCP tools with loading/error state
 */
export function useMCPTool<TArgs extends Record<string, unknown>, TResult>(
  toolName: string
) {
  const { client, connected } = useMCP()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<TResult | null>(null)

  const call = useCallback(async (args: TArgs): Promise<TResult | null> => {
    if (!connected) {
      setError('Not connected to MCP server')
      return null
    }

    setLoading(true)
    setError(null)

    try {
      const response = await client.callTool(toolName, args)
      if (response.isError) {
        const errorText = response.content.find((c) => c.type === 'text')?.text
        throw new Error(errorText ?? 'Tool call failed')
      }
      const text = response.content.find((c) => c.type === 'text')?.text
      if (!text) {
        setResult(null)
        return null
      }
      try {
        const parsed = JSON.parse(text) as TResult
        setResult(parsed)
        return parsed
      } catch {
        throw new Error(`Invalid JSON response: ${text.slice(0, 100)}`)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [client, connected, toolName])

  const reset = useCallback(() => {
    setResult(null)
    setError(null)
  }, [])

  return { call, loading, error, result, reset }
}

/**
 * Hook for reading MCP resources
 */
export function useMCPResource(uri: string) {
  const { client, connected } = useMCP()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [content, setContent] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!connected) {
      setError('Not connected to MCP server')
      return null
    }

    setLoading(true)
    setError(null)

    try {
      const contents = await client.readResource(uri)
      const text = contents.find((c) => c.text)?.text ?? null
      setContent(text)
      return text
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to read resource'
      setError(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [client, connected, uri])

  return { fetch, loading, error, content }
}

/**
 * Hook for wizard workflow management
 */
export function useMCPWizard() {
  const { client, connected } = useMCP()
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [currentStep, setCurrentStep] = useState<number>(0)
  const [totalSteps, setTotalSteps] = useState<number>(0)
  const [stepInfo, setStepInfo] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [complete, setComplete] = useState(false)
  const [answers, setAnswers] = useState<Record<string, unknown>>({})

  const start = useCallback(async (preset?: string) => {
    if (!connected) {
      setError('Not connected to MCP server')
      return false
    }

    setLoading(true)
    setError(null)
    setComplete(false)
    setAnswers({})

    try {
      const result = await client.wizardStart(preset)
      setSessionId(result.session_id)
      setCurrentStep(result.current_step)
      setTotalSteps(result.total_steps as number ?? 0)
      setStepInfo(result.current_step_info as Record<string, unknown> ?? null)
      if (result.current_answers) {
        setAnswers(result.current_answers as Record<string, unknown>)
      }
      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start wizard')
      return false
    } finally {
      setLoading(false)
    }
  }, [client, connected])

  const step = useCallback(async (stepAnswers: Record<string, unknown>, advance = true) => {
    if (!connected || !sessionId) {
      setError('No active wizard session')
      return false
    }

    setLoading(true)
    setError(null)

    try {
      const result = await client.wizardStep(sessionId, stepAnswers, advance)
      setCurrentStep(result.current_step)
      setComplete(result.is_complete)
      if (result.current_step_info) {
        setStepInfo(result.current_step_info as Record<string, unknown>)
      }
      if (result.current_answers) {
        setAnswers(result.current_answers as Record<string, unknown>)
      }
      if (result.validation_errors && (result.validation_errors as string[]).length > 0) {
        setError((result.validation_errors as string[]).join(', '))
      }
      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to advance wizard')
      return false
    } finally {
      setLoading(false)
    }
  }, [client, connected, sessionId])

  const generate = useCallback(async (destination?: string, force = false) => {
    if (!connected || !sessionId) {
      setError('No active wizard session')
      return null
    }

    setLoading(true)
    setError(null)

    try {
      const result = await client.wizardGenerate(sessionId, destination, force)
      if (result.success) {
        setSessionId(null)
        setComplete(true)
      } else {
        setError(result.message ?? 'Generation failed')
      }
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate project')
      return null
    } finally {
      setLoading(false)
    }
  }, [client, connected, sessionId])

  const cancel = useCallback(async () => {
    if (!sessionId) return

    try {
      await client.wizardCancel(sessionId)
    } finally {
      setSessionId(null)
      setCurrentStep(0)
      setComplete(false)
      setAnswers({})
      setError(null)
    }
  }, [client, sessionId])

  const reset = useCallback(() => {
    setSessionId(null)
    setCurrentStep(0)
    setTotalSteps(0)
    setStepInfo(null)
    setComplete(false)
    setAnswers({})
    setError(null)
  }, [])

  return {
    sessionId,
    currentStep,
    totalSteps,
    stepInfo,
    answers,
    loading,
    error,
    complete,
    start,
    step,
    generate,
    cancel,
    reset,
    active: !!sessionId && !complete,
  }
}
