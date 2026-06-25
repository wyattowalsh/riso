/** Copier answer keys removed from the public template surface. */

export const REMOVED_ANSWER_KEYS: Record<string, string> = {
  api_tracks: 'api_module + api_languages',
  api_language: 'api_languages',
  docs_site: 'docs_module + docs_framework',
  mcp_language: 'mcp_languages',
  saas_starter_module: 'saas_infra_module',
  saas_auth: 'saas_auth_module + saas_auth_provider',
  saas_billing: 'saas_billing_module + saas_billing_provider',
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
    (key) =>
      `${key}: removed answer key; use ${REMOVED_ANSWER_KEYS[key]}`,
  )
}
