import { useRisoStore, type RisoConfig } from '../../lib/store'
import {
  buildChoiceOptions,
  getPromptDefault,
  getPromptHelpSummary,
} from '../../lib/matrixData'
import { cn } from '../../lib/utils'

export function DocsConfig() {
  const { config, updateConfig } = useRisoStore()

  const docsSiteOptions = buildChoiceOptions({
    key: 'docs_site',
    fallbackChoices: ['fumadocs', 'sphinx-shibuya', 'docusaurus', 'none'],
    labels: {
      fumadocs: 'Fumadocs',
      'sphinx-shibuya': 'Sphinx Shibuya',
      docusaurus: 'Docusaurus',
      none: 'None',
    },
    descriptions: {
      fumadocs: 'Next.js-based, modern UI, AI-ready',
      'sphinx-shibuya': 'Python ecosystem, mature tooling',
      docusaurus: 'React-based, great for OSS projects',
      none: 'No documentation site',
    },
  })

  const selectedDocsSite =
    (config.docs_site ??
      getPromptDefault<RisoConfig['docs_site']>('docs_site', 'fumadocs')) as
      | RisoConfig['docs_site']
      | undefined

  const fumadocsSearchOptions = buildChoiceOptions({
    key: 'fumadocs_search_provider',
    fallbackChoices: ['orama', 'algolia', 'orama-cloud', 'none'],
    labels: {
      orama: 'Orama (free, self-hosted)',
      algolia: 'Algolia DocSearch',
      'orama-cloud': 'Orama Cloud',
      none: 'None',
    },
  })

  const fumadocsThemeOptions = buildChoiceOptions({
    key: 'fumadocs_theme',
    fallbackChoices: ['default', 'ocean', 'purple', 'custom'],
    labels: {
      default: 'Default',
      ocean: 'Ocean',
      purple: 'Purple',
      custom: 'Custom',
    },
  })

  const fumadocsCodeThemeOptions = buildChoiceOptions({
    key: 'fumadocs_code_theme',
    fallbackChoices: ['github', 'catppuccin', 'dracula', 'nord', 'one'],
    labels: {
      github: 'GitHub',
      catppuccin: 'Catppuccin',
      dracula: 'Dracula',
      nord: 'Nord',
      one: 'One',
    },
  })

  const fumadocsTocOptions = buildChoiceOptions({
    key: 'fumadocs_toc_depth',
    fallbackChoices: ['2', '3', '4'],
    labels: {
      '2': 'H2 only',
      '3': 'H2-H3',
      '4': 'H2-H4',
    },
  })

  const docusaurusSearchOptions = buildChoiceOptions({
    key: 'docusaurus_search_provider',
    fallbackChoices: ['local', 'algolia', 'typesense', 'none'],
    labels: {
      local: 'Local (offline)',
      algolia: 'Algolia DocSearch',
      typesense: 'Typesense',
      none: 'None',
    },
  })

  const docusaurusThemeOptions = buildChoiceOptions({
    key: 'docusaurus_theme',
    fallbackChoices: ['classic', 'tailwind'],
    labels: {
      classic: 'Classic (Infima CSS)',
      tailwind: 'Tailwind CSS',
    },
  })

  const docusaurusAnalyticsOptions = buildChoiceOptions({
    key: 'docusaurus_analytics',
    fallbackChoices: ['none', 'posthog', 'google', 'matomo'],
    labels: {
      none: 'None',
      posthog: 'PostHog',
      google: 'Google Analytics',
      matomo: 'Matomo',
    },
  })

  const docusaurusCommentsOptions = buildChoiceOptions({
    key: 'docusaurus_comments',
    fallbackChoices: ['none', 'giscus'],
    labels: {
      none: 'None',
      giscus: 'Giscus (GitHub)',
    },
  })

  const isFumadocs = selectedDocsSite === 'fumadocs'
  const isDocusaurus = selectedDocsSite === 'docusaurus'
  const isSphinxShibuya = selectedDocsSite === 'sphinx-shibuya'

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-display font-semibold text-gray-900 dark:text-white">Documentation</h2>
        <p className="mt-1 text-gray-500 dark:text-gray-400">
          Pick a docs stack and the features your team will rely on.
        </p>
      </div>

      {/* Docs Site Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Documentation Framework
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          {docsSiteOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => updateConfig({ docs_site: option.value as RisoConfig['docs_site'] })}
              className={cn(
                'p-5 rounded-2xl border text-left transition-all hover:-translate-y-0.5 hover:shadow-md',
                selectedDocsSite === option.value
                  ? 'border-riso-500 bg-riso-50/80 dark:bg-riso-900/20'
                  : 'border-white/70 dark:border-gray-700/60 bg-white/70 dark:bg-gray-900/60 hover:border-riso-300'
              )}
            >
              <div className="font-medium text-gray-900 dark:text-white">{option.label}</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">{option.description}</div>
            </button>
          ))}
        </div>
        {getPromptHelpSummary('docs_site') && (
          <p className="mt-2 text-xs text-gray-500">{getPromptHelpSummary('docs_site')}</p>
        )}
      </div>

      {/* Sphinx-Shibuya Info */}
      {isSphinxShibuya && (
        <div className="p-4 riso-card-soft rounded-xl">
          <h3 className="font-medium text-gray-900 dark:text-white mb-2">Sphinx Shibuya</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Sphinx with the Shibuya theme is auto-configured with sensible defaults.
            No additional options required.
          </p>
          <div className="mt-3 text-xs text-gray-500 dark:text-gray-500 space-y-1">
            <p>✓ Auto-generated API documentation from docstrings</p>
            <p>✓ Responsive Shibuya theme with dark mode</p>
            <p>✓ MyST markdown support</p>
            <p>✓ Cross-references and intersphinx</p>
          </div>
        </div>
      )}

      {/* Fumadocs Options */}
      {isFumadocs && (
        <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
          <h3 className="font-medium text-gray-900 dark:text-white">Fumadocs Options</h3>

          <div className="grid gap-4 sm:grid-cols-2">
            <SelectField
              label="Search Provider"
              value={
                config.fumadocs_search_provider ||
                getPromptDefault<RisoConfig['fumadocs_search_provider']>('fumadocs_search_provider', 'orama') ||
                'orama'
              }
              onChange={(v) => updateConfig({ fumadocs_search_provider: v as RisoConfig['fumadocs_search_provider'] })}
              options={fumadocsSearchOptions}
            />

            <SelectField
              label="Theme"
              value={
                config.fumadocs_theme ||
                getPromptDefault<RisoConfig['fumadocs_theme']>('fumadocs_theme', 'default') ||
                'default'
              }
              onChange={(v) => updateConfig({ fumadocs_theme: v as RisoConfig['fumadocs_theme'] })}
              options={fumadocsThemeOptions}
            />

            <SelectField
              label="Code Theme"
              value={
                config.fumadocs_code_theme ||
                getPromptDefault<RisoConfig['fumadocs_code_theme']>('fumadocs_code_theme', 'github') ||
                'github'
              }
              onChange={(v) => updateConfig({ fumadocs_code_theme: v as RisoConfig['fumadocs_code_theme'] })}
              options={fumadocsCodeThemeOptions}
            />

            <SelectField
              label="TOC Depth"
              value={
                config.fumadocs_toc_depth ||
                getPromptDefault<RisoConfig['fumadocs_toc_depth']>('fumadocs_toc_depth', '3') ||
                '3'
              }
              onChange={(v) => updateConfig({ fumadocs_toc_depth: v as RisoConfig['fumadocs_toc_depth'] })}
              options={fumadocsTocOptions}
            />
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <ToggleCheckbox
              label="llms.txt"
              checked={
                (config.fumadocs_llms_txt ??
                  getPromptDefault<'enabled' | 'disabled'>('fumadocs_llms_txt', 'enabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ fumadocs_llms_txt: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="OpenAPI Docs"
              checked={
                (config.fumadocs_openapi ??
                  getPromptDefault<'enabled' | 'disabled'>('fumadocs_openapi', 'enabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ fumadocs_openapi: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Blog"
              checked={
                (config.fumadocs_blog ??
                  getPromptDefault<'enabled' | 'disabled'>('fumadocs_blog', 'disabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ fumadocs_blog: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Mermaid"
              checked={
                (config.fumadocs_mermaid ??
                  getPromptDefault<'enabled' | 'disabled'>('fumadocs_mermaid', 'disabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ fumadocs_mermaid: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Math (KaTeX)"
              checked={
                (config.fumadocs_math ??
                  getPromptDefault<'enabled' | 'disabled'>('fumadocs_math', 'disabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ fumadocs_math: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Image Zoom"
              checked={
                (config.fumadocs_image_zoom ??
                  getPromptDefault<'enabled' | 'disabled'>('fumadocs_image_zoom', 'enabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ fumadocs_image_zoom: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Last Updated"
              checked={
                (config.fumadocs_last_updated ??
                  getPromptDefault<'enabled' | 'disabled'>('fumadocs_last_updated', 'enabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ fumadocs_last_updated: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Edit on GitHub"
              checked={
                (config.fumadocs_edit_on_github ??
                  getPromptDefault<'enabled' | 'disabled'>('fumadocs_edit_on_github', 'enabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ fumadocs_edit_on_github: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="i18n"
              checked={
                (config.fumadocs_i18n ??
                  getPromptDefault<'enabled' | 'disabled'>('fumadocs_i18n', 'disabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ fumadocs_i18n: v ? 'enabled' : 'disabled' })}
            />
          </div>
        </div>
      )}

      {/* Docusaurus Options */}
      {isDocusaurus && (
        <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
          <h3 className="font-medium text-gray-900 dark:text-white">Docusaurus Options</h3>

          <div className="grid gap-4 sm:grid-cols-2">
            <SelectField
              label="Search Provider"
              value={
                config.docusaurus_search_provider ||
                getPromptDefault<RisoConfig['docusaurus_search_provider']>('docusaurus_search_provider', 'local') ||
                'local'
              }
              onChange={(v) => updateConfig({ docusaurus_search_provider: v as RisoConfig['docusaurus_search_provider'] })}
              options={docusaurusSearchOptions}
            />

            <SelectField
              label="Theme"
              value={
                config.docusaurus_theme ||
                getPromptDefault<RisoConfig['docusaurus_theme']>('docusaurus_theme', 'classic') ||
                'classic'
              }
              onChange={(v) => updateConfig({ docusaurus_theme: v as RisoConfig['docusaurus_theme'] })}
              options={docusaurusThemeOptions}
            />

            <SelectField
              label="Analytics"
              value={
                config.docusaurus_analytics ||
                getPromptDefault<RisoConfig['docusaurus_analytics']>('docusaurus_analytics', 'none') ||
                'none'
              }
              onChange={(v) => updateConfig({ docusaurus_analytics: v as RisoConfig['docusaurus_analytics'] })}
              options={docusaurusAnalyticsOptions}
            />

            <SelectField
              label="Comments"
              value={
                config.docusaurus_comments ||
                getPromptDefault<RisoConfig['docusaurus_comments']>('docusaurus_comments', 'none') ||
                'none'
              }
              onChange={(v) => updateConfig({ docusaurus_comments: v as RisoConfig['docusaurus_comments'] })}
              options={docusaurusCommentsOptions}
            />
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <ToggleCheckbox
              label="llms.txt"
              checked={
                (config.docusaurus_llms_txt ??
                  getPromptDefault<'enabled' | 'disabled'>('docusaurus_llms_txt', 'enabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ docusaurus_llms_txt: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Faster (Rspack)"
              checked={
                (config.docusaurus_faster ??
                  getPromptDefault<'enabled' | 'disabled'>('docusaurus_faster', 'enabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ docusaurus_faster: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Blog"
              checked={
                (config.docusaurus_blog ??
                  getPromptDefault<'enabled' | 'disabled'>('docusaurus_blog', 'enabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ docusaurus_blog: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Mermaid"
              checked={
                (config.docusaurus_mermaid ??
                  getPromptDefault<'enabled' | 'disabled'>('docusaurus_mermaid', 'enabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ docusaurus_mermaid: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Math (KaTeX)"
              checked={
                (config.docusaurus_math ??
                  getPromptDefault<'enabled' | 'disabled'>('docusaurus_math', 'disabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ docusaurus_math: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Versioning"
              checked={
                (config.docusaurus_versioning ??
                  getPromptDefault<'enabled' | 'disabled'>('docusaurus_versioning', 'disabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ docusaurus_versioning: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="PWA"
              checked={
                (config.docusaurus_pwa ??
                  getPromptDefault<'enabled' | 'disabled'>('docusaurus_pwa', 'disabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ docusaurus_pwa: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="i18n"
              checked={
                (config.docusaurus_i18n ??
                  getPromptDefault<'enabled' | 'disabled'>('docusaurus_i18n', 'disabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ docusaurus_i18n: v ? 'enabled' : 'disabled' })}
            />
            <ToggleCheckbox
              label="Sitemap"
              checked={
                (config.docusaurus_sitemap ??
                  getPromptDefault<'enabled' | 'disabled'>('docusaurus_sitemap', 'enabled')) ===
                'enabled'
              }
              onChange={(v) => updateConfig({ docusaurus_sitemap: v ? 'enabled' : 'disabled' })}
            />
          </div>
        </div>
      )}
    </div>
  )
}

function SelectField({
  label,
  value,
  onChange,
  options
}: {
  label: string
  value: string
  onChange: (value: string) => void
  options: { value: string; label: string }[]
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white focus:border-riso-500 focus:ring-riso-500"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  )
}

function ToggleCheckbox({
  label,
  checked,
  onChange
}: {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  return (
    <label className="flex items-center gap-2 cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 rounded border-gray-300 text-riso-500 focus:ring-riso-500"
      />
      <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
    </label>
  )
}
