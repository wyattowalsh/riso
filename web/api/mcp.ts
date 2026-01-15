import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { WebStandardStreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js'
import { z } from 'zod'

// @ts-expect-error - JSON import works at runtime
import matrixData from '../src/data/matrix-data.json'

const server = new McpServer({
  name: 'riso-mcp',
  version: '1.0.0',
})

// Tool: Get template metadata
server.tool('get_template_info', 'Get Riso template metadata and defaults', {}, async () => {
  const info = {
    metadata: matrixData.template?.metadata || {},
    defaults: matrixData.template?.defaults || {},
  }
  return {
    content: [{ type: 'text', text: JSON.stringify(info, null, 2) }],
  }
})

// Tool: Get prompt details
server.tool(
  'get_prompt',
  'Get details for a specific prompt/configuration option',
  { key: z.string().describe('Prompt key (e.g., "project_name", "api_tracks")') },
  async ({ key }) => {
    const prompts = matrixData.template?.prompts || []
    const prompt = prompts.find((p: { key: string }) => p.key === key)
    if (!prompt) {
      return { content: [{ type: 'text', text: `Prompt "${key}" not found` }], isError: true }
    }
    return { content: [{ type: 'text', text: JSON.stringify(prompt, null, 2) }] }
  }
)

// Tool: List all prompts
server.tool(
  'list_prompts',
  'List all available configuration prompts',
  {},
  async () => {
    const prompts = matrixData.template?.prompts || []
    const summary = prompts.map((p: { key: string; type?: string; help?: string }) => ({
      key: p.key,
      type: p.type,
      help: p.help?.split('\n')[0],
    }))
    return { content: [{ type: 'text', text: JSON.stringify(summary, null, 2) }] }
  }
)

// Tool: Validate answers
server.tool(
  'validate_answers',
  'Validate a set of wizard answers',
  { answers: z.record(z.string(), z.unknown()).describe('Answers object to validate') },
  async ({ answers }) => {
    const prompts = matrixData.template?.prompts || []
    const errors: string[] = []

    for (const prompt of prompts) {
      const p = prompt as { key: string; required?: boolean }
      if (p.required && !(p.key in answers)) {
        errors.push(`Missing required field: ${p.key}`)
      }
    }

    return {
      content: [{ type: 'text', text: JSON.stringify({ valid: errors.length === 0, errors }, null, 2) }],
    }
  }
)

// Tool: Generate copier command
server.tool(
  'generate_command',
  'Generate the copier command for given answers',
  {
    answers: z.record(z.string(), z.unknown()).describe('Wizard answers'),
    destination: z.string().describe('Output directory'),
  },
  async ({ answers, destination }) => {
    const answerFlags = Object.entries(answers)
      .map(([k, v]) => `--data ${k}=${JSON.stringify(v)}`)
      .join(' ')

    const command = `copier copy gh:wyattowalsh/riso ${destination} ${answerFlags}`
    return { content: [{ type: 'text', text: command }] }
  }
)

// Resource: Full matrix data
server.resource('riso://matrix', 'Full template matrix data', async () => ({
  contents: [{ uri: 'riso://matrix', mimeType: 'application/json', text: JSON.stringify(matrixData) }],
}))

// Resource: Sample configs
const samples = ['default', 'full-stack', 'monorepo'] as const
for (const sample of samples) {
  server.resource(`riso://samples/${sample}`, `${sample} sample configuration`, async () => {
    const sampleData = (matrixData as Record<string, unknown>).samples as Record<string, unknown> | undefined
    const config = sampleData?.[sample] || {}
    return {
      contents: [{ uri: `riso://samples/${sample}`, mimeType: 'application/json', text: JSON.stringify(config) }],
    }
  })
}

// Create Edge-compatible transport
const sessions = new Map<string, WebStandardStreamableHTTPServerTransport>()

export default async function handler(req: Request): Promise<Response> {
  // Get or create session
  const sessionId = req.headers.get('mcp-session-id') || crypto.randomUUID()

  let transport = sessions.get(sessionId)
  if (!transport) {
    transport = new WebStandardStreamableHTTPServerTransport({ sessionIdGenerator: () => sessionId })
    sessions.set(sessionId, transport)
    await server.connect(transport)
  }

  return transport.handleRequest(req)
}

export const config = {
  runtime: 'edge',
}
