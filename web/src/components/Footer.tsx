import { Github, BookOpen, Sparkles } from 'lucide-react'

export function Footer() {
  return (
    <footer className="mt-16 border-t border-white/60 dark:border-gray-800/80 bg-white/70 dark:bg-gray-950/70 backdrop-blur">
      <div className="container mx-auto max-w-6xl px-4 py-10 flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-gray-900 dark:text-white">
            <Sparkles className="h-4 w-4 text-riso-500" />
            <span className="font-semibold">Riso</span>
          </div>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Build smarter project templates with confidence.
          </p>
        </div>
        <div className="flex items-center gap-4 text-sm font-medium text-gray-600 dark:text-gray-300">
          <a href="#wizard" className="hover:text-riso-600 dark:hover:text-riso-400">Configurator</a>
          <a href="/docs/" className="inline-flex items-center gap-2 hover:text-riso-600 dark:hover:text-riso-400">
            <BookOpen className="h-4 w-4" />
            Docs
          </a>
          <a
            href="https://github.com/wyattowalsh/riso"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 hover:text-riso-600 dark:hover:text-riso-400"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
        </div>
      </div>
    </footer>
  )
}
