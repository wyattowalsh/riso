import { useState, useMemo, useCallback } from 'react'
import { ChevronRight, ChevronDown, File, Folder, FolderOpen, Search } from 'lucide-react'
import { type RisoConfig } from '../lib/store'
import { cn } from '../lib/utils'

export interface FileNode {
  name: string
  path: string
  type: 'file' | 'folder'
  children?: FileNode[]
  size?: number
  highlight?: boolean
  extension?: string
  language?: string
  module?: string
}

interface FileTreeItemProps {
  node: FileNode
  depth: number
  expanded: Set<string>
  onToggle: (path: string) => void
  searchTerm: string
}

interface FileTreePreviewProps {
  config: Partial<RisoConfig>
  className?: string
}

const LANGUAGE_COLORS: Record<string, string> = {
  python: 'text-riso-sunflower',
  rust: 'text-riso-orange',
  go: 'text-riso-teal',
  typescript: 'text-riso-cornflower',
  node: 'text-riso-green',
  javascript: 'text-riso-sunflower',
  json: 'text-gray-400',
  yaml: 'text-riso-grape',
  toml: 'text-riso-orange',
  markdown: 'text-riso-cornflower',
}

const MODULE_BADGES: Record<string, { bg: string; text: string }> = {
  cli: { bg: 'bg-riso-federal-blue/20', text: 'text-riso-federal-blue dark:text-riso-cornflower' },
  api: { bg: 'bg-riso-green/20', text: 'text-riso-green dark:text-riso-mint' },
  mcp: { bg: 'bg-riso-grape/20', text: 'text-riso-grape dark:text-riso-fluorescent-pink' },
  docs: { bg: 'bg-riso-fluorescent-pink/20', text: 'text-riso-fluorescent-pink' },
  saas: { bg: 'bg-riso-orange/20', text: 'text-riso-orange dark:text-riso-apricot' },
}

function getFileExtension(filename: string): string {
  const parts = filename.split('.')
  return parts.length > 1 ? parts[parts.length - 1] : ''
}

function getLanguageFromExtension(ext: string): string | undefined {
  const extMap: Record<string, string> = {
    py: 'python',
    rs: 'rust',
    go: 'go',
    ts: 'typescript',
    tsx: 'typescript',
    js: 'javascript',
    jsx: 'javascript',
    json: 'json',
    yml: 'yaml',
    yaml: 'yaml',
    toml: 'toml',
    md: 'markdown',
    mdx: 'markdown',
  }
  return extMap[ext]
}

function estimateFileSize(filename: string, language?: string): number {
  if (filename.endsWith('.json')) return 1024
  if (filename.endsWith('.toml') || filename.endsWith('.yml')) return 512
  if (filename.endsWith('.md')) return 2048
  if (language === 'python') return 1536
  if (language === 'rust') return 2048
  if (language === 'typescript') return 1024
  if (language === 'go') return 1536
  return 512
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function calculateStats(tree: FileNode[]): { fileCount: number; folderCount: number; totalSize: number } {
  let fileCount = 0
  let folderCount = 0
  let totalSize = 0

  function traverse(nodes: FileNode[]) {
    for (const node of nodes) {
      if (node.type === 'folder') {
        folderCount++
        if (node.children) {
          traverse(node.children)
        }
      } else {
        fileCount++
        totalSize += node.size || 0
      }
    }
  }

  traverse(tree)
  return { fileCount, folderCount, totalSize }
}

function FileTreeItem({ node, depth, expanded, onToggle, searchTerm }: FileTreeItemProps) {
  const isExpanded = expanded.has(node.path)
  const isFolder = node.type === 'folder'
  const matchesSearch = !searchTerm || node.path.toLowerCase().includes(searchTerm.toLowerCase())

  const hasMatchingChildren = useMemo(() => {
    if (!isFolder || !node.children) return false

    function checkChildren(children: FileNode[]): boolean {
      return children.some(child => {
        if (child.path.toLowerCase().includes(searchTerm.toLowerCase())) return true
        if (child.type === 'folder' && child.children) {
          return checkChildren(child.children)
        }
        return false
      })
    }

    return checkChildren(node.children)
  }, [isFolder, node.children, searchTerm])

  if (!matchesSearch && !hasMatchingChildren) return null

  const fileExt = !isFolder ? getFileExtension(node.name) : ''
  const fileLang = node.language || getLanguageFromExtension(fileExt)

  return (
    <div>
      <div
        className={cn(
          'flex items-center py-1 px-2 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors',
          node.highlight && 'bg-indigo-50 dark:bg-indigo-900/20 border-l-2 border-indigo-500',
          matchesSearch && searchTerm && 'bg-yellow-50 dark:bg-yellow-900/10'
        )}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={() => isFolder && onToggle(node.path)}
      >
        {isFolder ? (
          <>
            {isExpanded ? (
              <ChevronDown className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
            ) : (
              <ChevronRight className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
            )}
            {isExpanded ? (
              <FolderOpen className={cn(
                'h-4 w-4 flex-shrink-0 ml-1',
                fileLang ? LANGUAGE_COLORS[fileLang] : 'text-riso-sunflower'
              )} />
            ) : (
              <Folder className={cn(
                'h-4 w-4 flex-shrink-0 ml-1',
                fileLang ? LANGUAGE_COLORS[fileLang] : 'text-riso-sunflower'
              )} />
            )}
          </>
        ) : (
          <>
            <span className="w-3.5" />
            <File className={cn(
              'h-4 w-4 flex-shrink-0 ml-1',
              fileLang ? LANGUAGE_COLORS[fileLang] : 'text-gray-400'
            )} />
          </>
        )}
        <span className={cn(
          'ml-2 text-sm truncate',
          node.highlight && 'font-medium text-indigo-600 dark:text-indigo-400',
          isFolder ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-400'
        )}>
          {node.name}
        </span>
        {node.module && MODULE_BADGES[node.module] && (
          <span className={cn(
            'text-[10px] px-1.5 py-0.5 rounded-full ml-1 flex-shrink-0',
            MODULE_BADGES[node.module].bg,
            MODULE_BADGES[node.module].text
          )}>
            {node.module}
          </span>
        )}
        {node.size && (
          <span className="ml-auto text-xs text-gray-400 flex-shrink-0">
            {formatFileSize(node.size)}
          </span>
        )}
      </div>
      {isFolder && isExpanded && node.children?.map(child => (
        <FileTreeItem
          key={child.path}
          node={child}
          depth={depth + 1}
          expanded={expanded}
          onToggle={onToggle}
          searchTerm={searchTerm}
        />
      ))}
    </div>
  )
}

function buildFileTree(config: Partial<RisoConfig>): FileNode[] {
  const projectName = config.project_name || 'my-project'
  const root: FileNode = {
    name: projectName,
    path: projectName,
    type: 'folder',
    children: [],
  }

  function addFile(name: string, parent: FileNode = root, language?: string, module?: string): FileNode {
    const path = `${parent.path}/${name}`
    const ext = getFileExtension(name)
    const fileLang = language || getLanguageFromExtension(ext)
    const file: FileNode = {
      name,
      path,
      type: 'file',
      extension: ext,
      language: fileLang,
      module,
      size: estimateFileSize(name, fileLang),
    }
    parent.children = parent.children || []
    parent.children.push(file)
    return file
  }

  function addFolder(name: string, parent: FileNode = root, language?: string, module?: string): FileNode {
    const path = `${parent.path}/${name}`
    const folder: FileNode = {
      name,
      path,
      type: 'folder',
      children: [],
      language,
      module,
    }
    parent.children = parent.children || []
    parent.children.push(folder)
    return folder
  }

  // Shared config files
  addFile('.gitignore', root)
  addFile('README.md', root)

  const taskRunner = config.task_runner || 'just'
  if (taskRunner === 'just' || taskRunner === 'both') {
    addFile('justfile', root)
  }
  if (taskRunner === 'makefile' || taskRunner === 'both') {
    addFile('Makefile', root)
  }

  // CI/CD
  if (config.ci_platform === 'github-actions') {
    const github = addFolder('.github', root)
    const workflows = addFolder('workflows', github)
    addFile('ci.yml', workflows, 'yaml')
    addFile('release.yml', workflows, 'yaml')
  }

  // AI Tools
  if (config.ai_tools_module === 'enabled') {
    const claude = addFolder('.claude', root)
    addFile('CLAUDE.md', claude, 'markdown')
    addFile('settings.json', claude, 'json')
  }

  // CLI Module - supports multiple languages
  if (config.cli_module === 'enabled') {
    const cliLangs = config.cli_languages || ['python']
    if (cliLangs.includes('python')) {
      addFile('pyproject.toml', root, 'python')
      const src = addFolder('src', root, 'python', 'cli')
      const pkg = addFolder(projectName.replace(/-/g, '_'), src, 'python')
      addFile('__init__.py', pkg, 'python')
      addFile('cli.py', pkg, 'python')
      addFile('main.py', pkg, 'python')
    }
    if (cliLangs.includes('rust')) {
      addFile('Cargo.toml', root, 'rust')
      const src = addFolder('src-rust', root, 'rust', 'cli')
      addFile('main.rs', src, 'rust')
      addFile('cli.rs', src, 'rust')
      addFile('lib.rs', src, 'rust')
    }
    if (cliLangs.includes('go')) {
      addFile('go.mod', root, 'go')
      const cmd = addFolder('cmd', root, 'go', 'cli')
      addFile('root.go', cmd, 'go')
      addFile('version.go', cmd, 'go')
      const internal = addFolder('internal', root, 'go')
      const configFolder = addFolder('config', internal, 'go')
      addFile('config.go', configFolder, 'go')
    }
    if (cliLangs.includes('typescript')) {
      if (!cliLangs.includes('python') && !cliLangs.includes('go') && !cliLangs.includes('rust')) {
        addFile('package.json', root, 'typescript')
      }
      addFile('tsconfig.json', root, 'json')
      const src = addFolder('src-ts', root, 'typescript', 'cli')
      addFile('index.ts', src, 'typescript')
      addFile('cli.ts', src, 'typescript')
      const commands = addFolder('commands', src, 'typescript')
      addFile('index.ts', commands, 'typescript')
    }
  }

  // API Module - supports multiple languages
  if (config.api_module === 'enabled') {
    const apiLangs = config.api_languages || ['python']
    const cliLangs = config.cli_languages || []
    if (apiLangs.includes('python')) {
      if (config.cli_module !== 'enabled' || !cliLangs.includes('python')) {
        addFile('pyproject.toml', root, 'python')
      }
      const api = addFolder('api', root, 'python', 'api')
      addFile('__init__.py', api, 'python')
      addFile('main.py', api, 'python')
      const routes = addFolder('routes', api, 'python')
      addFile('__init__.py', routes, 'python')
      addFile('health.py', routes, 'python')
      const models = addFolder('models', api, 'python')
      addFile('__init__.py', models, 'python')
    }
    if (apiLangs.includes('node')) {
      addFile('package.json', root, 'node')
      const apps = addFolder('apps', root)
      const api = addFolder('api', apps, 'node', 'api')
      const src = addFolder('src', api, 'typescript')
      addFile('index.ts', src, 'typescript')
      const routes = addFolder('routes', src, 'typescript')
      addFile('health.ts', routes, 'typescript')
    }
    if (apiLangs.includes('go')) {
      if (config.cli_module !== 'enabled' || !cliLangs.includes('go')) {
        addFile('go.mod', root, 'go')
      }
      const apiFolder = addFolder('api-go', root, 'go', 'api')
      addFile('main.go', apiFolder, 'go')
      const handlers = addFolder('handlers', apiFolder, 'go')
      addFile('health.go', handlers, 'go')
      const middleware = addFolder('middleware', apiFolder, 'go')
      addFile('auth.go', middleware, 'go')
    }
    if (apiLangs.includes('rust')) {
      if (config.cli_module !== 'enabled' || !cliLangs.includes('rust')) {
        addFile('Cargo.toml', root, 'rust')
      }
      const apiFolder = addFolder('api-rust', root, 'rust', 'api')
      const src = addFolder('src', apiFolder, 'rust')
      addFile('main.rs', src, 'rust')
      addFile('routes.rs', src, 'rust')
      addFile('handlers.rs', src, 'rust')
    }
  }

  // MCP Module - supports multiple languages
  if (config.mcp_module === 'enabled') {
    const mcpLangs = config.mcp_languages || ['python']
    if (mcpLangs.includes('python')) {
      const mcp = addFolder('mcp', root, 'python', 'mcp')
      addFile('server.py', mcp, 'python')
      const tools = addFolder('tools', mcp, 'python')
      addFile('__init__.py', tools, 'python')
      const resources = addFolder('resources', mcp, 'python')
      addFile('__init__.py', resources, 'python')
    }
    if (mcpLangs.includes('typescript')) {
      const mcp = addFolder('mcp-ts', root, 'typescript', 'mcp')
      addFile('server.ts', mcp, 'typescript')
      const tools = addFolder('tools', mcp, 'typescript')
      addFile('index.ts', tools, 'typescript')
      const resources = addFolder('resources', mcp, 'typescript')
      addFile('index.ts', resources, 'typescript')
    }
    if (mcpLangs.includes('rust')) {
      const mcp = addFolder('mcp-rust', root, 'rust', 'mcp')
      addFile('Cargo.toml', mcp, 'rust')
      const src = addFolder('src', mcp, 'rust')
      addFile('main.rs', src, 'rust')
      addFile('server.rs', src, 'rust')
    }
    if (mcpLangs.includes('go')) {
      const mcp = addFolder('mcp-go', root, 'go', 'mcp')
      addFile('go.mod', mcp, 'go')
      addFile('main.go', mcp, 'go')
      addFile('server.go', mcp, 'go')
    }
  }

  // Documentation Module
  if (config.docs_module === 'enabled') {
    const docs = addFolder('docs', root, undefined, 'docs')
    const framework = config.docs_framework || 'fumadocs'

    if (framework === 'fumadocs') {
      const app = addFolder('app', docs, 'typescript')
      addFile('layout.tsx', app, 'typescript')
      addFile('page.tsx', app, 'typescript')
      const content = addFolder('content', docs)
      const contentDocs = addFolder('docs', content)
      addFile('index.mdx', contentDocs, 'markdown')
      addFile('package.json', docs, 'json')
    } else if (framework === 'docusaurus') {
      const docsContent = addFolder('docs', docs)
      addFile('intro.md', docsContent, 'markdown')
      const blog = addFolder('blog', docs)
      addFile('welcome.md', blog, 'markdown')
      addFile('docusaurus.config.ts', docs, 'typescript')
      addFile('package.json', docs, 'json')
    } else if (framework === 'sphinx-shibuya') {
      const source = addFolder('source', docs, 'python')
      addFile('conf.py', source, 'python')
      addFile('index.rst', source, 'markdown')
      addFile('Makefile', docs)
    }
  }

  // SaaS Module
  if (config.saas_infra_module === 'enabled') {
    const webPath = config.project_layout === 'monorepo' ? 'apps/web' : 'web'
    const parts = webPath.split('/')
    let current = root
    for (const part of parts) {
      const existing = current.children?.find(c => c.name === part)
      if (existing && existing.type === 'folder') {
        current = existing
      } else {
        current = addFolder(part, current, undefined, 'saas')
      }
    }

    const web = current
    const app = addFolder('app', web, 'typescript')
    addFile('layout.tsx', app, 'typescript')
    addFile('page.tsx', app, 'typescript')
    const components = addFolder('components', web, 'typescript')
    const ui = addFolder('ui', components, 'typescript')
    addFile('button.tsx', ui, 'typescript')
    const lib = addFolder('lib', web, 'typescript')
    addFile('utils.ts', lib, 'typescript')

    if (config.saas_orm === 'prisma') {
      const prisma = addFolder('prisma', web)
      addFile('schema.prisma', prisma)
    } else if (config.saas_orm === 'drizzle') {
      const drizzle = addFolder('drizzle', web, 'typescript')
      addFile('schema.ts', drizzle, 'typescript')
    }

    if (config.project_layout === 'monorepo') {
      addFile('pnpm-workspace.yaml', root, 'yaml')
    }
  }

  // Tests folder
  const tests = addFolder('tests', root)
  addFile('test_main.py', tests, 'python')

  return [root]
}

export function FileTreePreview({ config, className }: FileTreePreviewProps) {
  const [expanded, setExpanded] = useState<Set<string>>(() => {
    const projectName = config.project_name || 'my-project'
    return new Set([projectName, `${projectName}/src`, `${projectName}/.github`])
  })
  const [searchTerm, setSearchTerm] = useState('')

  const fileTree = useMemo(() => buildFileTree(config), [config])
  const stats = useMemo(() => calculateStats(fileTree), [fileTree])

  const handleToggle = useCallback((path: string) => {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }, [])

  const expandAll = useCallback(() => {
    const allPaths = new Set<string>()
    function collectPaths(nodes: FileNode[]) {
      for (const node of nodes) {
        if (node.type === 'folder') {
          allPaths.add(node.path)
          if (node.children) {
            collectPaths(node.children)
          }
        }
      }
    }
    collectPaths(fileTree)
    setExpanded(allPaths)
  }, [fileTree])

  const collapseAll = useCallback(() => {
    const projectName = config.project_name || 'my-project'
    setExpanded(new Set([projectName]))
  }, [config.project_name])

  return (
    <div className={cn('riso-card p-4 rounded-xl', className)}>
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-gray-900 dark:text-white">
          Expected Project Structure
        </h4>
        <div className="flex items-center gap-2">
          <button
            onClick={expandAll}
            className="text-xs text-riso-federal-blue hover:underline"
          >
            Expand All
          </button>
          <span className="text-gray-400">|</span>
          <button
            onClick={collapseAll}
            className="text-xs text-riso-federal-blue hover:underline"
          >
            Collapse All
          </button>
        </div>
      </div>

      <div className="mb-3 relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Filter files..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-riso-federal-blue/20"
        />
      </div>

      <div className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
        <div className="max-h-96 overflow-y-auto font-mono text-xs">
          {fileTree.map(node => (
            <FileTreeItem
              key={node.path}
              node={node}
              depth={0}
              expanded={expanded}
              onToggle={handleToggle}
              searchTerm={searchTerm}
            />
          ))}
        </div>
        <div className="px-3 py-2 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 text-xs text-gray-500">
          {stats.fileCount} files, {stats.folderCount} folders • ~{formatFileSize(stats.totalSize)}
        </div>
      </div>
    </div>
  )
}
