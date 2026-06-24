import type { RisoConfig } from '../../lib/store'

/** Category tags for filtering presets */
export type PresetTag =
  | 'python'
  | 'node'
  | 'rust'
  | 'go'
  | 'cli'
  | 'api'
  | 'saas'
  | 'docs'
  | 'mcp'
  | 'monorepo'
  | 'single-package'
  | 'beginner'
  | 'intermediate'
  | 'advanced'
  | 'fullstack'
  | 'backend'
  | 'ai-ml'

/** Complexity level for the preset */
export type Complexity = 'beginner' | 'intermediate' | 'advanced'

/** File tree node for visualization */
export interface FileTreeNode {
  name: string
  type: 'file' | 'folder'
  children?: FileTreeNode[]
  description?: string
}

export interface Preset {
  id: string
  name: string
  /** Short tagline for cards */
  description: string
  /** Detailed explanation of purpose */
  purpose: string
  /** When should someone choose this preset? */
  useWhen: string[]
  /** Category tags for filtering */
  tags: PresetTag[]
  /** Complexity level */
  complexity: Complexity
  /** Key technologies included */
  techStack: string[]
  /** Example file tree structure */
  fileTree: FileTreeNode[]
  /** Approximate number of files generated */
  estimatedFiles: number
  icon: React.ReactNode
  config: Partial<RisoConfig>
}

export const PRESET_ACCENTS: Record<string, string> = {
  'minimal-python': 'card-minimal',
  'python-api': 'card-api',
  'fullstack': 'card-fullstack',
  'saas-starter': 'card-saas',
  'docs-only': 'card-docs',
  'rust-cli-python-api': 'card-rust',
  'typescript-mcp': 'card-mcp',
  'graphql-api': 'card-graphql',
  'microservices': 'card-micro',
  'ml-ai-project': 'card-ai',
  'go-api': 'card-go',
  'polyglot-monorepo': 'card-poly',
  'enterprise-saas': 'card-enterprise',
}

export const ICON_GRADIENTS: Record<string, string> = {
  'minimal-python': 'from-riso-federal-blue/20 to-riso-cornflower/20',
  'python-api': 'from-riso-green/20 to-riso-teal/20',
  'fullstack': 'from-riso-grape/20 to-riso-fluorescent-pink/20',
  'saas-starter': 'from-riso-orange/20 to-riso-sunflower/20',
  'docs-only': 'from-riso-fluorescent-pink/20 to-riso-burgundy/20',
  'rust-cli-python-api': 'from-riso-orange/20 to-riso-brick/20',
  'typescript-mcp': 'from-riso-cornflower/20 to-riso-federal-blue/20',
  'graphql-api': 'from-riso-fluorescent-pink/20 to-riso-grape/20',
  'microservices': 'from-riso-teal/20 to-riso-green/20',
  'ml-ai-project': 'from-riso-grape/20 to-riso-federal-blue/20',
  'go-api': 'from-riso-teal/20 to-riso-mint/20',
  'polyglot-monorepo': 'from-riso-sunflower/20 to-riso-orange/20',
  'enterprise-saas': 'from-riso-federal-blue/20 to-riso-burgundy/20',
}

export const ICON_TEXT: Record<string, string> = {
  'minimal-python': 'text-riso-federal-blue dark:text-riso-cornflower',
  'python-api': 'text-riso-green dark:text-riso-mint',
  'fullstack': 'text-riso-grape dark:text-riso-fluorescent-pink',
  'saas-starter': 'text-riso-orange dark:text-riso-apricot',
  'docs-only': 'text-riso-fluorescent-pink dark:text-riso-fluorescent-pink',
  'rust-cli-python-api': 'text-riso-orange dark:text-riso-apricot',
  'typescript-mcp': 'text-riso-cornflower dark:text-riso-cornflower',
  'graphql-api': 'text-riso-fluorescent-pink dark:text-riso-grape',
  'microservices': 'text-riso-teal dark:text-riso-mint',
  'ml-ai-project': 'text-riso-grape dark:text-riso-cornflower',
  'go-api': 'text-riso-teal dark:text-riso-mint',
  'polyglot-monorepo': 'text-riso-sunflower dark:text-riso-orange',
  'enterprise-saas': 'text-riso-federal-blue dark:text-riso-burgundy',
}
