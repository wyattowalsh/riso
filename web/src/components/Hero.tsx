import { ArrowRight, BookOpen, Sparkles, Terminal } from 'lucide-react'
import { getPromptChoices, matrixMeta, matrixPromptCount } from '../lib/matrixData'

export function Hero() {
  const docsChoices = getPromptChoices('docs_site', ['fumadocs', 'sphinx-shibuya', 'docusaurus', 'none'])
  const docsCount = docsChoices.filter((choice) => choice !== 'none').length
  const versionLabel = matrixMeta.templateVersion === 'unknown'
    ? 'Template'
    : `v${matrixMeta.templateVersion}`

  return (
    <section className="relative overflow-hidden riso-card p-6 sm:p-10 animate-fade-up">
      <div className="absolute -top-24 -right-20 h-56 w-56 rounded-full bg-riso-200/50 blur-3xl dark:bg-riso-900/40" />
      <div className="absolute -bottom-24 -left-20 h-56 w-56 rounded-full bg-orange-200/50 blur-3xl dark:bg-orange-900/40" />

      <div className="grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
        <div>
          <span className="riso-pill">
            <Sparkles className="h-3.5 w-3.5 text-riso-500" />
            Riso Template Builder
          </span>
          <h1 className="mt-6 text-4xl sm:text-5xl lg:text-6xl font-display font-semibold text-gray-900 dark:text-white leading-tight">
            Design a project blueprint that ships fast, feels cohesive, and stays maintainable.
          </h1>
          <p className="mt-4 text-base sm:text-lg text-gray-600 dark:text-gray-300 max-w-2xl">
            Riso assembles Python, Node, and docs stacks with a single guided flow. Tune quality gates,
            CI, and modules, then export a ready-to-run Copier command or answers file.
          </p>

          <div className="mt-6 flex flex-col sm:flex-row gap-3">
            <a
              href="#wizard"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-riso-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-riso-500/20 transition hover:bg-riso-600"
            >
              Start Configuring
              <ArrowRight className="h-4 w-4" />
            </a>
            <a
              href="/docs/"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-200/80 dark:border-gray-700/70 bg-white/80 dark:bg-gray-900/70 px-6 py-3 text-sm font-semibold text-gray-700 dark:text-gray-200 transition hover:border-riso-300 hover:text-riso-600 dark:hover:text-riso-400"
            >
              <BookOpen className="h-4 w-4" />
              Read the Docs
            </a>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-3 text-sm text-gray-500 dark:text-gray-400">
            <div className="rounded-xl border border-gray-200/70 dark:border-gray-700/60 bg-white/70 dark:bg-gray-900/60 px-4 py-3">
              <div className="text-lg font-semibold text-gray-900 dark:text-white">{versionLabel}</div>
              <div>Template version</div>
            </div>
            <div className="rounded-xl border border-gray-200/70 dark:border-gray-700/60 bg-white/70 dark:bg-gray-900/60 px-4 py-3">
              <div className="text-lg font-semibold text-gray-900 dark:text-white">{matrixPromptCount}+</div>
              <div>Configuration prompts</div>
            </div>
            <div className="rounded-xl border border-gray-200/70 dark:border-gray-700/60 bg-white/70 dark:bg-gray-900/60 px-4 py-3">
              <div className="text-lg font-semibold text-gray-900 dark:text-white">{docsCount} docs</div>
              <div>Stacks to choose from</div>
            </div>
          </div>
        </div>

        <div className="relative">
          <div className="riso-card-soft p-5 sm:p-6">
            <div className="flex items-center justify-between">
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">
                CLI Preview
              </div>
              <Terminal className="h-4 w-4 text-riso-500" />
            </div>
            <pre className="mt-4 text-sm leading-relaxed bg-gray-900 text-gray-100 rounded-xl p-4 overflow-x-auto">
              <code>{`copier copy gh:wyattowalsh/riso ./my-project \\
  --data project_layout=monorepo \\
  --data quality_profile=strict \\
  --data docs_site=fumadocs`}</code>
            </pre>
            <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
              Export this command or download a <code className="text-gray-900 dark:text-gray-100">copier-answers.yml</code>.
            </p>
          </div>

          <div className="absolute -right-6 -bottom-8 hidden sm:block riso-card-soft px-4 py-3 animate-float">
            <div className="text-xs font-semibold text-gray-900 dark:text-white">Instant presets</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Jump to review in one click.</div>
          </div>
        </div>
      </div>
    </section>
  )
}
