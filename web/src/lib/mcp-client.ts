/**
 * MCP Client for Riso Web App
 * 
 * Connects to the Riso MCP server via SSE transport for real-time
 * template operations directly from the browser.
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js'

export interface MCPClientConfig {
  /** MCP server URL (default: http://localhost:3000) */
  serverUrl?: string
  /** SSE endpoint path (default: /sse) */
  ssePath?: string
  /** Connection timeout in ms (not yet implemented) */
  timeout?: number
}

export interface ToolResult {
  content: Array<{ type: string; text?: string; data?: unknown }>
  isError?: boolean
}

export interface ResourceContent {
  uri: string
  mimeType?: string
  text?: string
  blob?: string
}

export interface PromptMessage {
  role: 'user' | 'assistant'
  content: { type: string; text: string }
}

class RisoMCPClient {
  private client: Client | null = null
  private transport: SSEClientTransport | null = null
  private config: Required<MCPClientConfig>
  private _connected = false

  constructor(config: MCPClientConfig = {}) {
    this.config = {
      serverUrl: config.serverUrl ?? 'http://localhost:3000',
      ssePath: config.ssePath ?? '/sse',
      timeout: config.timeout ?? 30000,
    }
  }

  get connected(): boolean {
    return this._connected
  }

  get serverUrl(): string {
    return this.config.serverUrl
  }

  /**
   * Connect to the MCP server
   */
  async connect(): Promise<void> {
    if (this._connected) return

    try {
      const sseUrl = new URL(this.config.ssePath, this.config.serverUrl)
      this.transport = new SSEClientTransport(sseUrl)

      this.client = new Client(
        { name: 'riso-web', version: '1.0.0' },
        { capabilities: {} }
      )

      await this.client.connect(this.transport)
      this._connected = true
    } catch (error) {
      this._connected = false
      throw new Error(`Failed to connect to MCP server: ${error}`)
    }
  }

  /**
   * Disconnect from the MCP server
   */
  async disconnect(): Promise<void> {
    if (!this._connected) return

    try {
      await this.client?.close()
    } finally {
      this.client = null
      this.transport = null
      this._connected = false
    }
  }

  /**
   * List available tools
   */
  async listTools(): Promise<Array<{ name: string; description?: string }>> {
    this.ensureConnected()
    const result = await this.client!.listTools()
    return result.tools.map((t) => ({ name: t.name, description: t.description }))
  }

  /**
   * List available resources
   */
  async listResources(): Promise<Array<{ uri: string; name?: string; mimeType?: string }>> {
    this.ensureConnected()
    const result = await this.client!.listResources()
    return result.resources.map((r) => ({
      uri: r.uri,
      name: r.name,
      mimeType: r.mimeType,
    }))
  }

  /**
   * List available prompts
   */
  async listPrompts(): Promise<Array<{ name: string; description?: string }>> {
    this.ensureConnected()
    const result = await this.client!.listPrompts()
    return result.prompts.map((p) => ({ name: p.name, description: p.description }))
  }

  /**
   * Call a tool with arguments
   */
  async callTool(name: string, args: Record<string, unknown> = {}): Promise<ToolResult> {
    this.ensureConnected()
    const result = await this.client!.callTool({ name, arguments: args })
    return {
      content: result.content as ToolResult['content'],
      isError: result.isError === true,
    }
  }

  /**
   * Read a resource by URI
   */
  async readResource(uri: string): Promise<ResourceContent[]> {
    this.ensureConnected()
    const result = await this.client!.readResource({ uri })
    return result.contents.map((c) => ({
      uri: c.uri,
      mimeType: c.mimeType,
      text: 'text' in c ? c.text : undefined,
      blob: 'blob' in c ? c.blob : undefined,
    }))
  }

  /**
   * Get a prompt with arguments
   */
  async getPrompt(name: string, args: Record<string, string> = {}): Promise<PromptMessage[]> {
    this.ensureConnected()
    const result = await this.client!.getPrompt({ name, arguments: args })
    return result.messages.map((m) => ({
      role: m.role,
      content: m.content as { type: string; text: string },
    }))
  }

  // === Riso-specific convenience methods ===

  /**
   * Start a new wizard session
   */
  async wizardStart(preset?: string): Promise<{ session_id: string; current_step: number; [key: string]: unknown }> {
    const result = await this.callTool('wizard_start', preset ? { template_variant: preset } : {})
    const text = result.content.find((c) => c.type === 'text')?.text
    if (!text) return { session_id: '', current_step: 0 }
    try {
      return JSON.parse(text)
    } catch {
      throw new Error(`Invalid wizard_start response: ${text}`)
    }
  }

  /**
   * Advance wizard with answers (uses wizard_step, not wizard_next)
   */
  async wizardStep(
    sessionId: string,
    answers: Record<string, unknown>,
    advance = true
  ): Promise<{ is_complete: boolean; current_step: number; [key: string]: unknown }> {
    const result = await this.callTool('wizard_step', { 
      session_id: sessionId, 
      answers,
      advance 
    })
    const text = result.content.find((c) => c.type === 'text')?.text
    if (!text) return { is_complete: false, current_step: 0 }
    try {
      return JSON.parse(text)
    } catch {
      throw new Error(`Invalid wizard_step response: ${text}`)
    }
  }

  /**
   * Get current wizard state (uses wizard_status)
   */
  async wizardStatus(sessionId: string): Promise<Record<string, unknown>> {
    const result = await this.callTool('wizard_status', { session_id: sessionId })
    const text = result.content.find((c) => c.type === 'text')?.text
    if (!text) return {}
    try {
      return JSON.parse(text)
    } catch {
      throw new Error(`Invalid wizard_status response: ${text}`)
    }
  }

  /**
   * Generate project from completed wizard session
   */
  async wizardGenerate(
    sessionId: string,
    destination?: string,
    force = false
  ): Promise<{ success: boolean; destination?: string; message?: string }> {
    const result = await this.callTool('wizard_generate', { 
      session_id: sessionId,
      destination,
      force
    })
    const text = result.content.find((c) => c.type === 'text')?.text
    if (result.isError) {
      return { success: false, message: text }
    }
    if (!text) return { success: true }
    try {
      return JSON.parse(text)
    } catch {
      return { success: true, message: text }
    }
  }

  /**
   * Cancel a wizard session
   */
  async wizardCancel(sessionId: string): Promise<{ success: boolean; message?: string }> {
    const result = await this.callTool('wizard_cancel', { session_id: sessionId })
    const text = result.content.find((c) => c.type === 'text')?.text
    if (!text) return { success: true }
    try {
      return JSON.parse(text)
    } catch {
      return { success: true, message: text }
    }
  }

  /**
   * Get template catalog
   */
  async getTemplateCatalog(): Promise<unknown> {
    const contents = await this.readResource('riso://catalog/modules')
    const text = contents.find((c) => c.text)?.text
    if (!text) return {}
    try {
      return JSON.parse(text)
    } catch {
      return { raw: text }
    }
  }

  /**
   * Get sample configuration by name.
   * Known samples: 'default', 'full-stack', 'monorepo'
   * Use listSamples() to discover all available samples.
   */
  async getSampleConfig(sampleName: string): Promise<string> {
    const contents = await this.readResource(`riso://samples/${sampleName}/answers`)
    return contents.find((c) => c.text)?.text ?? ''
  }

  /**
   * List all available samples
   */
  async listSamples(): Promise<string> {
    const contents = await this.readResource('riso://samples')
    return contents.find((c) => c.text)?.text ?? ''
  }

  /**
   * Generate project with Copier directly (bypasses wizard)
   */
  async generateProject(
    destination: string,
    answers: Record<string, unknown>,
    options: { force?: boolean; vcsRef?: string } = {}
  ): Promise<{ success: boolean; destination?: string; message?: string }> {
    const result = await this.callTool('copier_copy', {
      destination,
      answers,
      force: options.force ?? false,
      vcs_ref: options.vcsRef,
    })
    const text = result.content.find((c) => c.type === 'text')?.text
    if (result.isError) {
      return { success: false, message: text }
    }
    if (!text) return { success: true, destination }
    try {
      return JSON.parse(text)
    } catch {
      return { success: true, destination, message: text }
    }
  }

  private ensureConnected(): void {
    if (!this._connected || !this.client) {
      throw new Error('MCP client not connected. Call connect() first.')
    }
  }
}

// Singleton instance
let clientInstance: RisoMCPClient | null = null

/**
 * Get or create the MCP client singleton
 */
export function getMCPClient(config?: MCPClientConfig): RisoMCPClient {
  if (!clientInstance) {
    clientInstance = new RisoMCPClient(config)
  }
  return clientInstance
}

/**
 * Reset the client (useful for testing or reconnecting with new config)
 */
export async function resetMCPClient(): Promise<void> {
  if (clientInstance) {
    await clientInstance.disconnect()
    clientInstance = null
  }
}

export { RisoMCPClient }
