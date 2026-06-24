import { ArrowRight, BookOpen, Sparkles, Terminal } from 'lucide-react'
import { matrixMeta, matrixPromptCount } from '../lib/matrixData'

export function Hero() {
  const versionLabel = matrixMeta.templateVersion === 'unknown'
    ? 'Template'
    : `v${matrixMeta.templateVersion}`

  return (
    <section aria-labelledby="hero-heading" className="relative overflow-hidden riso-card hero-gradient hero-section p-6 sm:p-10 animate-fade-up">
      <div className="grid min-w-0 gap-10 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)] lg:items-center">
        <div className="min-w-0">
          <span className="riso-pill animate-fade-up">
            <Sparkles className="h-3.5 w-3.5 text-riso-federal-blue dark:text-riso-cornflower" aria-hidden="true" />
            Project Generator
          </span>
          <h1 id="hero-heading" className="mt-6 display-xl break-words bg-gradient-to-r from-riso-federal-blue via-riso-teal to-riso-federal-blue bg-clip-text text-transparent animate-fade-up delay-100">
            Scaffold your next project in seconds.
          </h1>
          <p className="mt-4 text-base sm:text-lg text-gray-600 dark:text-gray-300 max-w-2xl animate-fade-up delay-200">
            Pick modules (CLI, API, MCP, docs, SaaS), configure options, and generate a full project structure. Uses <a href="https://copier.readthedocs.io" target="_blank" rel="noopener noreferrer" className="underline hover:text-riso-federal-blue dark:hover:text-riso-cornflower">Copier</a> under the hood.
          </p>

          <div className="mt-6 flex flex-col sm:flex-row gap-3 animate-fade-up delay-300">
            <a href="#wizard" className="btn-primary">
              Start configuring
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </a>
            <a href="/docs/" className="btn-secondary">
              <BookOpen className="h-4 w-4" aria-hidden="true" />
              Docs
            </a>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-3 text-sm text-gray-500 dark:text-gray-400 animate-fade-up delay-400">
            <div className="stat-card rounded-xl border border-gray-200/70 dark:border-gray-700/60 bg-white/80 dark:bg-gray-900/70 px-4 py-4 hover:border-riso-federal-blue/40 hover:scale-105 transition-all duration-300 backdrop-blur-sm">
              <div className="stat-value text-2xl">{matrixPromptCount}+</div>
              <div className="mt-1 text-xs uppercase tracking-wider">Options</div>
            </div>
            <div className="stat-card rounded-xl border border-gray-200/70 dark:border-gray-700/60 bg-white/80 dark:bg-gray-900/70 px-4 py-4 hover:border-riso-fluorescent-pink/40 hover:scale-105 transition-all duration-300 backdrop-blur-sm">
              <div className="stat-value text-2xl">13</div>
              <div className="mt-1 text-xs uppercase tracking-wider">Presets</div>
            </div>
            <div className="stat-card rounded-xl border border-gray-200/70 dark:border-gray-700/60 bg-white/80 dark:bg-gray-900/70 px-4 py-4 hover:border-riso-green/40 hover:scale-105 transition-all duration-300 backdrop-blur-sm">
              <div className="stat-value text-2xl">{versionLabel}</div>
              <div className="mt-1 text-xs uppercase tracking-wider">Template</div>
            </div>
          </div>
        </div>

        <div className="relative min-w-0">
          <div className="riso-card-soft max-w-full min-w-0 p-5 sm:p-6 animate-scale-in delay-200">
            <div className="flex items-center justify-between">
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">
                CLI Preview
              </div>
              <Terminal className="h-4 w-4 text-riso-federal-blue dark:text-riso-cornflower" aria-hidden="true" />
            </div>
            <pre className="mt-4 w-full max-w-full text-sm leading-relaxed bg-gray-900 text-gray-100 rounded-xl p-4 overflow-x-auto" aria-label="Example Copier command">
              <code>{`copier copy gh:wyattowalsh/riso ./my-project \\
  --data project_layout=monorepo \\
  --data quality_profile=strict \\
  --data docs_module=enabled \\
  --data docs_module=enabled \\
  --data docs_framework=fumadocs`}</code>
            </pre>
            <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
              Run this command to generate your project, or download the config file.
            </p>
          </div>

          <div className="absolute -right-6 -bottom-8 hidden sm:block riso-card-soft px-4 py-3 animate-float delay-500" aria-hidden="true">
            <div className="text-xs font-semibold text-gray-900 dark:text-white">Or use a preset</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Skip the wizard.</div>
          </div>
        </div>
      </div>
    </section>
  )
}
