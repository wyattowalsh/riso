import { BookOpen, ArrowUpRight, Sparkles, Library } from 'lucide-react'

export function DocsCallout() {
  return (
    <section className="riso-card p-6 sm:p-8">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <span className="riso-pill">
            <Library className="h-3.5 w-3.5 text-riso-500" />
            Documentation Hub
          </span>
          <h3 className="mt-4 text-2xl font-semibold text-gray-900 dark:text-white">
            Module guides, API references, and migration paths.
          </h3>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-300 max-w-2xl">
            Covers each module (CLI, API, MCP, Docs, SaaS), template customization, CI/CD setup, and upgrading.
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <a
            href="/docs/"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-gray-900 text-white px-5 py-3 text-sm font-semibold transition hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100"
          >
            <BookOpen className="h-4 w-4" />
            Open Docs
            <ArrowUpRight className="h-4 w-4" />
          </a>
          <a
            href="#wizard"
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-200/80 dark:border-gray-700/60 bg-white/80 dark:bg-gray-900/70 px-5 py-3 text-sm font-semibold text-gray-700 dark:text-gray-200 transition hover:border-riso-300 hover:text-riso-600 dark:hover:text-riso-400"
          >
            <Sparkles className="h-4 w-4" />
            Back to Builder
          </a>
        </div>
      </div>
    </section>
  )
}
