// Simple MCP info endpoint for Vercel
import type { VercelRequest, VercelResponse } from '@vercel/node'

export default function handler(req: VercelRequest, res: VercelResponse) {
  return res.json({
    name: 'riso-mcp',
    version: '1.0.0',
    status: 'ok',
    description: 'Riso MCP API - template configuration service',
    endpoints: {
      info: '/mcp',
    },
    repository: 'https://github.com/wyattowalsh/riso',
    docs: 'https://riso.build/docs/',
  })
}
