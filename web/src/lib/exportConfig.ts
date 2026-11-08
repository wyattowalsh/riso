import { stringify } from 'yaml'
import { validateProjectName } from '../components/steps/ProjectBasics'
import type { RisoConfig } from './store'
import { parseConfigOrThrow } from './configSchemas'

export type CopierArgs = Record<string, unknown>

/** Preserve every public Copier answer, including options not exposed by wizard controls. */
export function configToCopierArgs(
  config: Partial<RisoConfig> | Record<string, unknown>,
): CopierArgs {
  const src = parseConfigOrThrow(config)
  const args: CopierArgs = { ...src }
  if (!src.project_name) delete args.project_name
  if (src.api_features !== undefined) {
    args.api_features =
      src.api_features === 'none' || src.api_features === ''
        ? []
        : String(src.api_features).split(',')
  }
  return args
}

/** POSIX-safe single-quoted shell literal. */
export function shellEscapeString(value: string): string {
  return `'${value.replace(/'/g, `'\\''`)}'`
}

export function resolveExportProjectName(config: Partial<RisoConfig>): string {
  const parsed = parseConfigOrThrow(config)
  const candidate = (
    (parsed.project_name as string | undefined) || 'my-project'
  ).trim()
  const validation = validateProjectName(candidate)
  if (!validation.valid) {
    throw new Error(validation.error ?? 'Invalid project name for export')
  }
  return candidate
}

export function generateCliCommand(config: Partial<RisoConfig>): string {
  const projectName = resolveExportProjectName(config)
  const dest = shellEscapeString(`./${projectName}`)
  return [
    `# Download the YAML from this page as copier-answers.yml first.`,
    `uv run riso copy ${dest} --answers-file copier-answers.yml`,
  ].join('\n')
}

export function generateYamlConfig(
  config: Partial<RisoConfig> | Record<string, unknown>,
): string {
  const yamlObj = configToCopierArgs(config)
  const header = `# Riso Configuration
# Generated: ${new Date().toISOString()}
# Usage: uv run riso copy --answers-file copier-answers.yml

`
  return header + stringify(yamlObj)
}

export type GenerateResult =
  { ok: true; value: string } | { ok: false; error: string }

function catchGenerate(err: unknown): GenerateResult {
  return {
    ok: false,
    error: err instanceof Error ? err.message : String(err),
  }
}

/** Soft-fail wrapper so Review cannot crash the wizard on invalid names. */
export function tryGenerateCliCommand(
  config: Partial<RisoConfig>,
): GenerateResult {
  try {
    return { ok: true, value: generateCliCommand(config) }
  } catch (err) {
    return catchGenerate(err)
  }
}

export function tryGenerateYamlConfig(
  config: Partial<RisoConfig> | Record<string, unknown>,
): GenerateResult {
  try {
    return { ok: true, value: generateYamlConfig(config) }
  } catch (err) {
    return catchGenerate(err)
  }
}
