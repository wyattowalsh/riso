import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { WebStandardStreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js'
import { z } from 'zod'

// @ts-expect-error - JSON import works at runtime
import matrixData from '../src/data/matrix.json'

const server = new McpServer({
  name: 'riso-mcp',
  version: '1.0.0',
})

// Tool: Get module catalog
server.tool('get_modules', 'List all available Riso template modules', {}, async () => {
  const modules = matrixData.modules || []
  return {
    content: [{ type: 'text', text: JSON.stringify(modules, null, 2) }],
  }
})

// Tool: Get module details  
server.tool(
  'get_module',
  'Get details for a specific module',
  { name: z.string().describe('Module name') },
  async ({ name }) => {
    const modules = matrixData.modules || []
    const module = modules.find((m: { name: string }) => m.name === name)
    if (!module) {
      return { content: [{ type: 'text', text: `Module "${name}" not found` }], isError: true }
    }
    return { content: [{ type: 'text', text: JSON.stringify(module, null, 2) }] }
  }
)

// Tool: Get prompts for a step
server.tool(
  'get_step_prompts',
  'Get wizard prompts for a configuration step',
  { step: z.string().describe('Step name (e.g., "project", "api", "quality")') },
  async ({ step }) => {
    const prompts = matrixData.prompts || []
    const stepPrompts = prompts.filter((p: { group?: string }) => p.group === step)
    return { content: [{ type: 'text', text: JSON.stringify(stepPrompts, null, 2) }] }
  }
)

// Tool: Validate answers
server.tool(
  'validate_answers',
  'Validate a set of wizard answers',
  { answers: z.record(z.string(), z.unknown()).describe('Answers object to validate') },
  async ({ answers }) => {
    const prompts = matrixData.prompts || []
    const errors: string[] = []

    for (const prompt of prompts) {
      const p = prompt as { name: string; required?: boolean }
      if (p.required && !(p.name in answers)) {
        errors.push(`Missing required field: ${p.name}`)
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
