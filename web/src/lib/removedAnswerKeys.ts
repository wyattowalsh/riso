/** Copier answer keys removed from the public template surface. */

/** Keep in parity with `src/riso/core/removed_answer_keys.py`. */
export const REMOVED_ANSWER_KEYS: Record<string, string> = {
  api_tracks: '`api_module` plus `api_languages`',
  api_language: '`api_languages`',
  docs_site: '`docs_module` plus `docs_framework`',
  mcp_language: '`mcp_languages`',
  saas_starter_module: '`saas_infra_module`',
  saas_auth: '`saas_auth_module` plus `saas_auth_provider`',
  saas_billing: '`saas_billing_module` plus `saas_billing_provider`',
  include_admin: '`saas_admin_dashboard`',
}

export type RemapAction =
  | 'wrap-list'
  | 'derive'
  | 'rename'
  | 'split'
  | 'rename-bool'

export interface RemapOp {
  old: string
  new_keys: readonly string[]
  action: RemapAction
  before?: unknown
  after?: Record<string, unknown>
}

export interface RemapResult {
  answers: Record<string, unknown>
  ops: RemapOp[]
}

export const ANSWER_KEY_REMAPS: Record<string, RemapOp> = {
  api_tracks: {
    old: 'api_tracks',
    new_keys: ['api_module', 'api_languages'],
    action: 'derive',
  },
  api_language: {
    old: 'api_language',
    new_keys: ['api_languages'],
    action: 'wrap-list',
  },
  docs_site: {
    old: 'docs_site',
    new_keys: ['docs_module', 'docs_framework'],
    action: 'derive',
  },
  mcp_language: {
    old: 'mcp_language',
    new_keys: ['mcp_languages'],
    action: 'wrap-list',
  },
  saas_starter_module: {
    old: 'saas_starter_module',
    new_keys: ['saas_infra_module'],
    action: 'rename',
  },
  saas_auth: {
    old: 'saas_auth',
    new_keys: ['saas_auth_module', 'saas_auth_provider'],
    action: 'split',
  },
  saas_billing: {
    old: 'saas_billing',
    new_keys: ['saas_billing_module', 'saas_billing_provider'],
    action: 'split',
  },
  include_admin: {
    old: 'include_admin',
    new_keys: ['saas_admin_dashboard'],
    action: 'rename-bool',
  },
}

const TOKEN_SPLIT = /[\s,+/|]+/
const API_LANGUAGES = new Set(['python', 'node', 'rust', 'go'])
const MCP_LANGUAGES = new Set(['python', 'typescript', 'rust', 'go'])
const MCP_ALIASES: Record<string, string> = { node: 'typescript', js: 'typescript' }
const API_TRACK_ALIASES: Record<string, string> = {
  python: 'python',
  node: 'node',
  rust: 'rust',
  go: 'go',
  fastapi: 'python',
  fastify: 'node',
  actix: 'rust',
}
const API_TRACKS_OFF = new Set(['', 'none', 'disabled', '[]'])
const DOCS_SITE_OFF = new Set(['none', 'false', 'disabled', 'off'])
const DOCS_SITE_FRAMEWORKS: Record<string, string> = {
  sphinx: 'sphinx-shibuya',
  'sphinx-shibuya': 'sphinx-shibuya',
  docusaurus: 'docusaurus',
  fumadocs: 'fumadocs',
}
const SPLIT_OFF = new Set(['none', 'disabled', 'false', 'off'])
const SAAS_AUTH_PROVIDERS = new Set(['clerk', 'authjs'])
const SAAS_BILLING_PROVIDERS = new Set(['stripe', 'paddle', 'lemonsqueezy'])
const MODULE_ON = new Set(['enabled', 'true', 'yes', 'on', '1'])
const MODULE_OFF = new Set(['disabled', 'false', 'no', 'off', '0', 'none'])
const BOOL_TRUE = new Set(['true', 'yes', 'on', '1', 'enabled'])
const BOOL_FALSE = new Set(['false', 'no', 'off', '0', 'disabled', 'none', ''])

export class RemovedAnswerKeyError extends Error {
  readonly errors: string[]

  constructor(errors: string[]) {
    super(
      `Removed Copier answer keys are no longer supported:\n${errors
        .map((line) => `- ${line}`)
        .join('\n')}`,
    )
    this.name = 'RemovedAnswerKeyError'
    this.errors = errors
  }
}

function isNone(value: unknown): boolean {
  return value === null || value === undefined
}

function isSequence(value: unknown): value is unknown[] {
  return Array.isArray(value)
}

function normToken(value: unknown): string {
  if (isNone(value)) {
    return 'none'
  }
  return String(value).trim().toLowerCase()
}

function tokens(value: unknown): string[] {
  if (isNone(value)) {
    return []
  }
  if (isSequence(value)) {
    return value.map((item) => normToken(item)).filter((item) => item.length > 0)
  }
  const text = String(value).trim()
  if (!text) {
    return []
  }
  return text.toLowerCase().split(TOKEN_SPLIT).filter((part) => part.length > 0)
}

function wrapList(
  value: unknown,
  allowed: ReadonlySet<string>,
  aliases: Record<string, string> = {},
): string[] | null {
  if (isSequence(value)) {
    const out: string[] = []
    const seen = new Set<string>()
    for (const item of value) {
      const raw = String(item).trim()
      if (!raw) {
        continue
      }
      const mapped = aliases[raw.toLowerCase()] ?? raw.toLowerCase()
      const token = allowed.has(mapped) ? mapped : raw
      if (seen.has(token)) {
        continue
      }
      seen.add(token)
      out.push(token)
    }
    return out
  }
  if (typeof value === 'string') {
    const raw = value.trim()
    if (!raw) {
      return null
    }
    const mapped = aliases[raw.toLowerCase()] ?? raw.toLowerCase()
    if (!allowed.has(mapped)) {
      return null
    }
    return [mapped]
  }
  return null
}

function moduleToggle(value: unknown): string | null {
  if (typeof value === 'boolean') {
    return value ? 'enabled' : 'disabled'
  }
  if (typeof value === 'number' && (value === 0 || value === 1)) {
    return value === 1 ? 'enabled' : 'disabled'
  }
  const text = normToken(value)
  if (MODULE_ON.has(text)) {
    return 'enabled'
  }
  if (MODULE_OFF.has(text)) {
    return 'disabled'
  }
  return null
}

function asBool(value: unknown): boolean | null {
  if (typeof value === 'boolean') {
    return value
  }
  if (typeof value === 'number' && (value === 0 || value === 1)) {
    return Boolean(value)
  }
  if (typeof value === 'string') {
    const text = value.trim().toLowerCase()
    if (BOOL_TRUE.has(text)) {
      return true
    }
    if (BOOL_FALSE.has(text)) {
      return false
    }
  }
  return null
}

function isOff(value: unknown, offTokens: ReadonlySet<string>): boolean {
  if (isNone(value)) {
    return true
  }
  if (isSequence(value) && value.length === 0) {
    return true
  }
  if (typeof value === 'boolean') {
    return !value && offTokens.has('false')
  }
  return offTokens.has(normToken(value))
}

function mapApiLanguage(value: unknown): Record<string, unknown> | null {
  const wrapped = wrapList(value, API_LANGUAGES)
  if (wrapped === null) {
    return null
  }
  return { api_languages: wrapped }
}

function mapMcpLanguage(value: unknown): Record<string, unknown> | null {
  const wrapped = wrapList(value, MCP_LANGUAGES, MCP_ALIASES)
  if (wrapped === null) {
    return null
  }
  return { mcp_languages: wrapped }
}

function mapApiTracks(value: unknown): Record<string, unknown> | null {
  if (isOff(value, API_TRACKS_OFF)) {
    return { api_module: 'disabled' }
  }
  const langs: string[] = []
  const seen = new Set<string>()
  for (const token of tokens(value)) {
    const mapped = API_TRACK_ALIASES[token]
    if (!mapped || seen.has(mapped)) {
      continue
    }
    seen.add(mapped)
    langs.push(mapped)
  }
  if (langs.length === 0) {
    return null
  }
  return { api_module: 'enabled', api_languages: langs }
}

function mapDocsSite(value: unknown): Record<string, unknown> | null {
  if (isOff(value, DOCS_SITE_OFF)) {
    return { docs_module: 'disabled' }
  }
  if (isSequence(value)) {
    return null
  }
  const framework = DOCS_SITE_FRAMEWORKS[normToken(value)]
  if (!framework) {
    return null
  }
  return { docs_module: 'enabled', docs_framework: framework }
}

function mapSaasStarterModule(value: unknown): Record<string, unknown> | null {
  const toggle = moduleToggle(value)
  if (toggle === null) {
    return null
  }
  return { saas_infra_module: toggle }
}

function mapSplit(
  value: unknown,
  moduleKey: string,
  providerKey: string,
  providers: ReadonlySet<string>,
): Record<string, unknown> | null {
  if (isOff(value, SPLIT_OFF)) {
    return { [moduleKey]: 'disabled' }
  }
  if (isSequence(value)) {
    return null
  }
  const provider = normToken(value)
  if (!providers.has(provider)) {
    return null
  }
  return { [moduleKey]: 'enabled', [providerKey]: provider }
}

function mapSaasAuth(value: unknown): Record<string, unknown> | null {
  return mapSplit(value, 'saas_auth_module', 'saas_auth_provider', SAAS_AUTH_PROVIDERS)
}

function mapSaasBilling(value: unknown): Record<string, unknown> | null {
  return mapSplit(
    value,
    'saas_billing_module',
    'saas_billing_provider',
    SAAS_BILLING_PROVIDERS,
  )
}

function mapIncludeAdmin(value: unknown): Record<string, unknown> | null {
  const flag = asBool(value)
  if (flag === null) {
    return null
  }
  return { saas_admin_dashboard: flag }
}

const DEST_MAPPERS: Record<string, (value: unknown) => Record<string, unknown> | null> = {
  api_tracks: mapApiTracks,
  api_language: mapApiLanguage,
  docs_site: mapDocsSite,
  mcp_language: mapMcpLanguage,
  saas_starter_module: mapSaasStarterModule,
  saas_auth: mapSaasAuth,
  saas_billing: mapSaasBilling,
  include_admin: mapIncludeAdmin,
}

function writeDests(
  out: Record<string, unknown>,
  dests: Record<string, unknown>,
): Record<string, unknown> {
  const after: Record<string, unknown> = {}
  for (const [key, value] of Object.entries(dests)) {
    if (!(key in out)) {
      out[key] = value
    }
    after[key] = out[key]
  }
  return after
}

/** Apply known removed-key remaps. Leave unmapped leftovers for reject. */
export function applyRemovedKeyRemaps(
  answers: Record<string, unknown>,
): RemapResult {
  const out = { ...answers }
  const ops: RemapOp[] = []
  for (const [old, spec] of Object.entries(ANSWER_KEY_REMAPS)) {
    if (!(old in out)) {
      continue
    }
    const before = out[old]
    const dests = DEST_MAPPERS[old](before)
    if (dests === null) {
      continue
    }
    const after = writeDests(out, dests)
    delete out[old]
    ops.push({
      old,
      new_keys: spec.new_keys,
      action: spec.action,
      before,
      after,
    })
  }
  return { answers: out, ops }
}

/** Plan name for the TS remap twin (same contract as `applyRemovedKeyRemaps`). */
export function remapRemovedAnswerKeys(
  answers: Record<string, unknown>,
): RemapResult {
  return applyRemovedKeyRemaps(answers)
}

export function findRemovedAnswerKeys(
  config: Record<string, unknown>,
): string[] {
  return Object.keys(config)
    .filter((key) => key in REMOVED_ANSWER_KEYS)
    .sort()
}

export function formatRemovedAnswerKeyErrors(
  config: Record<string, unknown>,
): string[] {
  return findRemovedAnswerKeys(config).map(
    (key) => `${key}: removed answer key; use ${REMOVED_ANSWER_KEYS[key]}`,
  )
}

function formatPreviewValue(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.join(', ')}]`
  }
  if (typeof value === 'string') {
    return value
  }
  if (value === undefined) {
    return 'undefined'
  }
  return JSON.stringify(value)
}

export function formatRemapPreview(ops: RemapOp[]): string[] {
  return ops.map((op) => {
    const dests = Object.entries(op.after ?? {})
      .map(([key, value]) => `${key}=${formatPreviewValue(value)}`)
      .join(', ')
    return `${op.old}: ${formatPreviewValue(op.before)} → ${dests} (${op.action})`
  })
}

/** Apply remaps, then fail-closed on leftover removed keys or unmapped values. */
export function applyThenRejectRemovedKeys(
  answers: Record<string, unknown>,
): RemapResult {
  const result = applyRemovedKeyRemaps(answers)
  const leftover = formatRemovedAnswerKeyErrors(result.answers)
  if (leftover.length > 0) {
    throw new RemovedAnswerKeyError(leftover)
  }
  return result
}

/** Hydration helper: remap known keys and drop leftovers (never throw). */
export function dropLeftoverRemovedKeys(
  answers: Record<string, unknown>,
): Record<string, unknown> {
  const { answers: remapped } = applyRemovedKeyRemaps(answers)
  const out = { ...remapped }
  for (const key of findRemovedAnswerKeys(out)) {
    delete out[key]
  }
  return out
}
