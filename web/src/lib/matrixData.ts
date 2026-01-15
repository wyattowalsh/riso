import rawMatrixData from '../data/matrix-data.json'

type MatrixPrompt = {
  key: string
  type: string | null
  choices: string[] | null
  default: unknown
  when: string | null
  help: string | null
}

type MatrixData = {
  generated_at?: string
  template: {
    metadata?: {
      name?: string
      version?: string
      description?: string
    }
    defaults?: Record<string, unknown>
    prompts?: MatrixPrompt[]
  }
}

const matrixData = rawMatrixData as MatrixData

const promptEntries = matrixData.template.prompts ?? []
const promptMap = new Map(promptEntries.map((prompt) => [prompt.key, prompt]))

const valueLabelOverrides: Record<string, string> = {
  'python+node': 'Python + Node',
  'sphinx-shibuya': 'Sphinx Shibuya',
  'github-actions': 'GitHub Actions',
  'nextjs-16': 'Next.js 16',
  'remix-2': 'Remix 2.x',
  'orama-cloud': 'Orama Cloud',
  posthog: 'PostHog',
  authjs: 'Auth.js',
  'supabase-storage': 'Supabase Storage',
  openai: 'OpenAI',
  github: 'GitHub',
  llms: 'LLMs',
}

const matrixDefaults = matrixData.template.defaults ?? {}

function formatTitleCase(value: string): string {
  return value
    .replace(/\+/g, ' + ')
    .replace(/_/g, ' ')
    .replace(/-/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (match) => match.toUpperCase())
}

export const matrixMeta = {
  generatedAt: matrixData.generated_at,
  templateName: matrixData.template.metadata?.name ?? 'riso-template',
  templateVersion: matrixData.template.metadata?.version ?? 'unknown',
}

export const matrixPromptCount = promptEntries.length

export function getPrompt(key: string): MatrixPrompt | undefined {
  return promptMap.get(key)
}

export function getPromptChoices(key: string, fallback: string[] = []): string[] {
  const choices = promptMap.get(key)?.choices
  if (Array.isArray(choices) && choices.length > 0) {
    return choices
  }
  return fallback
}

export function getPromptDefault<T>(key: string, fallback?: T): T | undefined {
  if (Object.prototype.hasOwnProperty.call(matrixDefaults, key)) {
    return matrixDefaults[key] as T
  }
  return fallback
}

export function getPromptHelpSummary(key: string): string | undefined {
  const help = promptMap.get(key)?.help
  if (!help) return undefined
  const firstLine = help.split('\n').find((line) => line.trim() !== '')
  return firstLine?.trim()
}

export function formatChoiceLabel(value: string): string {
  return valueLabelOverrides[value] ?? formatTitleCase(value)
}

export function buildChoiceOptions(options: {
  key: string
  fallbackChoices?: string[]
  labels?: Record<string, string>
  descriptions?: Record<string, string>
}): { value: string; label: string; description?: string }[] {
  const choices = getPromptChoices(options.key, options.fallbackChoices ?? [])
  return choices.map((choice) => ({
    value: choice,
    label: options.labels?.[choice] ?? formatChoiceLabel(choice),
    description: options.descriptions?.[choice],
  }))
}

export function formatMatrixTimestamp(timestamp?: string): string | undefined {
  if (!timestamp) return undefined
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return timestamp
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export { matrixDefaults }
