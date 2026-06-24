import { Github, BookOpen, Sparkles } from 'lucide-react'

export function Footer() {
  return (
    <footer className="mt-16 border-t border-gray-200/50 dark:border-gray-800/50 bg-white/70 dark:bg-gray-950/70 backdrop-blur">
      <div className="container mx-auto max-w-6xl px-4 py-10 flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-gray-900 dark:text-white">
            <Sparkles className="h-4 w-4 text-riso-federal-blue dark:text-riso-cornflower" />
            <span className="font-semibold">Riso</span>
          </div>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Scaffold Python, TypeScript, Rust, and Go projects.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <a href="#wizard" className="text-sm text-gray-500 dark:text-gray-400 hover:text-riso-federal-blue dark:hover:text-riso-cornflower transition-colors">Configurator</a>
          <a href="/docs/" className="inline-flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 hover:text-riso-federal-blue dark:hover:text-riso-cornflower transition-colors">
            <BookOpen className="h-4 w-4" />
            Docs
          </a>
          <a
            href="https://github.com/wyattowalsh/riso"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 hover:text-riso-federal-blue dark:hover:text-riso-cornflower transition-colors"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
        </div>
      </div>
    </footer>
  )
}
