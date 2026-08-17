import { z } from 'zod'
import {
  applyThenRejectRemovedKeys,
  dropLeftoverRemovedKeys,
  findRemovedAnswerKeys,
  RemovedAnswerKeyError,
} from './removedAnswerKeys'

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
  })

export const customPresetSchema = z.object({
  name: z.string().min(1).max(120),
  description: z.string().max(500).optional(),
  config: shareConfigSchema,
  createdAt: z.string().min(1),
  // Legacy presets may omit version — coerce to 1 for migration.
  version: z.coerce.number().int().positive().default(1),
})

export const customPresetsRecordSchema = z.record(z.string(), customPresetSchema)

export type ParsedShareConfig = z.infer<typeof shareConfigSchema>
export type ParsedCustomPreset = z.infer<typeof customPresetSchema>

export function parseShareConfigPayload(
  raw: unknown,
): { success: true; data: ParsedShareConfig } | { success: false; error: string } {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    return { success: false, error: 'Invalid share configuration' }
  }
  try {
    const remapped = applyThenRejectRemovedKeys({
      ...(raw as Record<string, unknown>),
    })
    const result = shareConfigSchema.safeParse(remapped.answers)
    if (!result.success) {
      const message = result.error.issues.map((i) => i.message).join('; ')
      return { success: false, error: message || 'Invalid share configuration' }
    }
    return { success: true, data: result.data }
  } catch (error) {
    if (error instanceof RemovedAnswerKeyError) {
      return { success: false, error: error.message }
    }
    throw error
  }
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
    const remappedConfig = dropLeftoverRemovedKeys({ ...rawConfig })
    const withDefaults = entry
      ? {
          name: key,
          createdAt: new Date(0).toISOString(),
          version: 1,
          ...entry,
          config: remappedConfig,
        }
      : value
    const result = customPresetSchema.safeParse(withDefaults)
    if (result.success) {
      out[key] = result.data
    }
  }
  return out
}
