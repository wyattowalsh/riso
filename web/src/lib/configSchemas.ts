import { z } from 'zod'
import {
  applyThenRejectRemovedKeys,
  findRemovedAnswerKeys,
  RemovedAnswerKeyError,
} from './removedAnswerKeys'
import { getPrompt } from './matrixData'

function rejectRemovedKeys(
  value: Record<string, unknown>,
  ctx: z.RefinementCtx,
  pathPrefix = '',
): void {
  for (const key of findRemovedAnswerKeys(value)) {
    ctx.addIssue({
      code: 'custom',
      path: pathPrefix ? [pathPrefix, key] : [key],
      message: `Removed answer key: ${key}`,
    })
  }
}

/** Partial Copier answers embedded in share URLs. */
export const shareConfigSchema = z
  .record(z.string(), z.unknown())
  .superRefine((value, ctx) => {
    rejectRemovedKeys(value, ctx)
    for (const [key, answer] of Object.entries(value)) {
      const prompt = getPrompt(key)
      if (!prompt) {
        ctx.addIssue({
          code: 'custom',
          path: [key],
          message: `${key}: unknown Copier answer`,
        })
        continue
      }
      // The wizard represents API feature checkboxes as a comma token; Copier uses a list.
      const normalized =
        key === 'api_features' && typeof answer === 'string'
          ? answer === 'none' || answer === ''
            ? []
            : answer.split(',')
          : answer
      const isList = prompt.multiselect || key === 'python_versions'
      const validType = isList
        ? Array.isArray(normalized) &&
          normalized.every((item) => typeof item === 'string')
        : prompt.type === 'bool'
          ? typeof normalized === 'boolean'
          : typeof normalized === 'string'
      if (!validType) {
        const expected = isList
          ? 'a list of strings'
          : prompt.type === 'bool'
            ? 'a boolean'
            : 'a string'
        ctx.addIssue({
          code: 'custom',
          path: [key],
          message: `${key}: expected ${expected}`,
        })
        continue
      }
      const answers = isList ? (normalized as string[]) : [normalized as string]
      if (
        prompt.choices &&
        answers.some((item) => !prompt.choices!.includes(item))
      ) {
        ctx.addIssue({
          code: 'custom',
          path: [key],
          message: `${key}: unsupported choice`,
        })
      }
    }
  })
  .transform((value) => {
    if (Array.isArray(value.api_features)) {
      return { ...value, api_features: value.api_features.join(',') || 'none' }
    }
    return value
  })

export const customPresetSchema = z.object({
  name: z.string().min(1).max(120),
  description: z.string().max(500).optional(),
  config: shareConfigSchema,
  createdAt: z.string().min(1),
  // Legacy presets may omit version — coerce to 1 for migration.
  version: z.coerce.number().int().positive().default(1),
})

export const customPresetsRecordSchema = z.record(
  z.string(),
  customPresetSchema,
)

export type ParsedShareConfig = z.infer<typeof shareConfigSchema>
export type ParsedCustomPreset = z.infer<typeof customPresetSchema>

export function parseShareConfigPayload(
  raw: unknown,
):
  | { success: true; data: ParsedShareConfig }
  | { success: false; error: string } {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    return { success: false, error: 'Invalid share configuration' }
  }
  try {
    // Copier persists source/revision metadata alongside answers; it is not wizard state.
    const answers = Object.fromEntries(
      Object.entries(raw).filter(([key]) => !key.startsWith('_')),
    )
    const remapped = applyThenRejectRemovedKeys(answers)
    const result = shareConfigSchema.safeParse(remapped.answers)
    if (!result.success) {
      const message = result.error.issues.map((i) => i.message).join('; ')
      return {
        success: false,
        error: message || 'Invalid share configuration',
      }
    }
    return { success: true, data: result.data }
  } catch (error) {
    if (error instanceof RemovedAnswerKeyError) {
      return { success: false, error: error.message }
    }
    throw error
  }
}

export function parseConfigOrThrow(raw: unknown): ParsedShareConfig {
  const parsed = parseShareConfigPayload(raw)
  if (!parsed.success) throw new Error(parsed.error)
  return parsed.data
}

export function parseCustomPresetsStorage(
  raw: unknown,
): Record<string, ParsedCustomPreset> {
  if (!raw || typeof raw !== 'object') {
    return {}
  }
  // Soft-parse each preset so one bad entry does not drop the whole store.
  const out: Record<string, ParsedCustomPreset> = {}
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    const entry =
      value && typeof value === 'object' && !Array.isArray(value)
        ? (value as Record<string, unknown>)
        : null
    const rawConfig =
      entry &&
      entry.config &&
      typeof entry.config === 'object' &&
      !Array.isArray(entry.config)
        ? (entry.config as Record<string, unknown>)
        : {}
    if (
      entry &&
      'config' in entry &&
      (!entry.config ||
        typeof entry.config !== 'object' ||
        Array.isArray(entry.config))
    )
      continue
    const parsedConfig = parseShareConfigPayload(rawConfig)
    if (!parsedConfig.success) continue
    const withDefaults = entry
      ? {
          name: key,
          createdAt: new Date(0).toISOString(),
          version: 1,
          ...entry,
          config: parsedConfig.data,
        }
      : value
    const result = customPresetSchema.safeParse(withDefaults)
    if (result.success) {
      out[key] = result.data
    }
  }
  return out
}
