import { useRisoStore, type RisoConfig } from '../../lib/store'
import {
  buildChoiceOptions,
  getPromptDefault,
} from '../../lib/matrixData'
import { cn } from '../../lib/utils'
import { BookOpen, FileText, Code2, Sparkles } from 'lucide-react'

interface FrameworkOption {
  value: string
  label: string
  description: string
  icon: React.ElementType
  features: string[]
}

const FRAMEWORK_OPTIONS: FrameworkOption[] = [
  {
    value: 'fumadocs',
    label: 'Fumadocs',
    description: 'Next.js-based, modern UI, AI-ready',
    icon: Sparkles,
    features: ['Next.js 15+', 'Orama search', 'OpenAPI integration', 'llms.txt'],
  },
  {
    value: 'docusaurus',
    label: 'Docusaurus',
    description: 'React-based, great for OSS projects',
    icon: Code2,
    features: ['Rspack builds', 'Algolia/local search', 'Versioning', 'Blog'],
  },
  {
    value: 'sphinx-shibuya',
    label: 'Sphinx Shibuya',
    description: 'Python ecosystem, mature tooling',
    icon: FileText,
    features: ['Auto-generated API docs', 'MyST Markdown', 'Cross-references', 'Dark mode'],
  },
  {
    value: 'mkdocs',
    label: 'MkDocs Material',
    description: 'Markdown-first, Material Design',
    icon: BookOpen,
    features: ['Material theme', 'Search', 'Navigation tabs', 'Dark mode'],
  },
]

export function DocsConfig() {
  const { config, updateConfig } = useRisoStore()

  const docsEnabled = config.docs_module === 'enabled'
  const selectedFramework = config.docs_framework || 'fumadocs'

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

  const isFumadocs = selectedFramework === 'fumadocs'
  const isDocusaurus = selectedFramework === 'docusaurus'
  const isSphinxShibuya = selectedFramework === 'sphinx-shibuya'
  const isMkDocs = selectedFramework === 'mkdocs'

  const handleToggleDocs = (enabled: boolean) => {
    updateConfig({ docs_module: enabled ? 'enabled' : 'disabled' })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="display-md text-gray-900 dark:text-white">Documentation</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Pick a docs framework and the features your team will rely on.
        </p>
      </div>

      {/* Enable/Disable Toggle */}
      <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-riso-federal-blue/10 to-riso-cornflower/10 dark:from-riso-federal-blue/5 dark:to-riso-cornflower/5 border border-riso-federal-blue/20 dark:border-riso-federal-blue/10">
        <div>
          <h3 className="font-semibold text-gray-900 dark:text-white">Enable Documentation</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Add a documentation site to your project
          </p>
        </div>
        <button
          type="button"
          onClick={() => handleToggleDocs(!docsEnabled)}
          className={cn(
            'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out',
            docsEnabled
              ? 'bg-riso-federal-blue dark:bg-riso-teal'
              : 'bg-gray-200 dark:bg-gray-600'
          )}
        >
          <span
            className={cn(
              'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
              docsEnabled ? 'translate-x-5' : 'translate-x-0'
            )}
          />
        </button>
      </div>

      {docsEnabled && (
        <>
          {/* Docs Framework Selection */}
          <div>
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-3">
              Documentation Framework
            </h3>
            <div className="grid gap-3 sm:grid-cols-2">
              {FRAMEWORK_OPTIONS.map((option) => {
                const Icon = option.icon
                const isSelected = selectedFramework === option.value
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() =>
                      updateConfig({ docs_framework: option.value as RisoConfig['docs_framework'] })
                    }
                    className={cn(
                      'p-4 rounded-xl border-2 text-left transition-all',
                      isSelected
                        ? 'border-riso-federal-blue dark:border-riso-teal bg-riso-federal-blue/5 dark:bg-riso-teal/10'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={cn(
                          'p-2 rounded-lg',
                          isSelected
                            ? 'bg-riso-federal-blue/10 dark:bg-riso-teal/20'
                            : 'bg-gray-100 dark:bg-gray-700'
                        )}
                      >
                        <Icon
                          className={cn(
                            'h-5 w-5',
                            isSelected
                              ? 'text-riso-federal-blue dark:text-riso-teal'
                              : 'text-gray-400'
                          )}
                        />
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-900 dark:text-white">
                          {option.label}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                          {option.description}
                        </div>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {option.features.map((feature) => (
                            <span
                              key={feature}
                              className="text-xs px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
                            >
                              {feature}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Sphinx-Shibuya Info */}
          {isSphinxShibuya && (
            <div className="rounded-xl bg-gray-50/50 dark:bg-gray-800/30 p-4 border border-gray-200 dark:border-gray-700">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-2">
                Sphinx Shibuya
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Sphinx with the Shibuya theme is auto-configured with sensible defaults. No
                additional options required.
              </p>
              <div className="mt-4 grid gap-2 sm:grid-cols-2">
                {[
                  'Auto-generated API documentation from docstrings',
                  'Responsive Shibuya theme with dark mode',
                  'MyST markdown support',
                  'Cross-references and intersphinx',
                ].map((feature) => (
                  <p
                    key={feature}
                    className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2"
                  >
                    <span className="text-riso-green dark:text-riso-mint font-semibold mt-0.5">
                      ✓
                    </span>
                    {feature}
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* MkDocs Info */}
          {isMkDocs && (
            <div className="rounded-xl bg-gray-50/50 dark:bg-gray-800/30 p-4 border border-gray-200 dark:border-gray-700">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-2">
                MkDocs Material
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                MkDocs with the Material theme provides a clean, modern documentation experience.
              </p>
              <div className="mt-4 grid gap-2 sm:grid-cols-2">
                {[
                  'Material Design theme',
                  'Built-in search',
                  'Navigation tabs',
                  'Dark mode support',
                ].map((feature) => (
                  <p
                    key={feature}
                    className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2"
                  >
                    <span className="text-riso-green dark:text-riso-mint font-semibold mt-0.5">
                      ✓
                    </span>
                    {feature}
                  </p>
                ))}
              </div>
            </div>
          )}

      {/* Fumadocs Options */}
      {isFumadocs && (
        <div className="rounded-xl bg-gray-50/50 dark:bg-gray-800/30 p-5 space-y-5">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white">Fumadocs Options</h3>

          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Core Configuration</h4>
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
          </div>

          <div className="border-t border-gray-200 dark:border-gray-700"></div>

          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Optional Features</h4>
            <div className="grid gap-2 sm:grid-cols-3">
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
        </div>
      )}

      {/* Docusaurus Options */}
      {isDocusaurus && (
        <div className="rounded-xl bg-gray-50/50 dark:bg-gray-800/30 p-5 space-y-5">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white">Docusaurus Options</h3>

          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Core Configuration</h4>
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
          </div>

          <div className="border-t border-gray-200 dark:border-gray-700"></div>

          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Optional Features</h4>
            <div className="grid gap-2 sm:grid-cols-3">
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
        </div>
      )}
        </>
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
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white focus:border-riso-federal-blue dark:focus:border-riso-teal focus:ring-riso-federal-blue dark:focus:ring-riso-teal transition-colors"
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
    <label className="flex items-center gap-3 cursor-pointer p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 rounded border-gray-300 text-riso-federal-blue dark:text-riso-teal focus:ring-riso-federal-blue dark:focus:ring-riso-teal transition-all"
      />
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</span>
    </label>
  )
}
