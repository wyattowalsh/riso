import { BookOpen, Github, Moon, Sparkles, Sun } from 'lucide-react'
import { useState, useEffect } from 'react'
import { formatMatrixTimestamp, matrixMeta } from '../lib/matrixData'

const DARK_MODE_KEY = 'riso-dark-mode'

export function Header() {
  const [darkMode, setDarkMode] = useState(() => {
    // Check localStorage first, then system preference
    const saved = localStorage.getItem(DARK_MODE_KEY)
    if (saved !== null) return saved === 'true'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    // Persist preference
    localStorage.setItem(DARK_MODE_KEY, String(darkMode))
    
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  const matrixStamp = formatMatrixTimestamp(matrixMeta.generatedAt)

  return (
    <header className="sticky top-0 z-50 border-b border-white/70 dark:border-gray-800/80 bg-white/70 dark:bg-gray-950/70 backdrop-blur">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/90 dark:bg-gray-900/80 border border-white/70 dark:border-gray-800/60 shadow-sm">
              <img src="/riso.svg" alt="Riso" className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl font-display font-semibold text-gray-900 dark:text-white">Riso</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">Project Template Configurator</p>
              <p className="text-[11px] text-gray-400 dark:text-gray-500">
                Matrix snapshot {matrixStamp ?? 'unknown'} · Template {matrixMeta.templateVersion}
              </p>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-600 dark:text-gray-300">
            <a href="#wizard" className="inline-flex items-center gap-2 hover:text-riso-600 dark:hover:text-riso-400">
              <Sparkles className="h-4 w-4" />
              Builder
            </a>
            <a href="/docs/" className="inline-flex items-center gap-2 hover:text-riso-600 dark:hover:text-riso-400">
              <BookOpen className="h-4 w-4" />
              Docs
            </a>
          </nav>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-lg text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100 hover:bg-white/80 dark:hover:bg-gray-900/80 transition-colors"
              aria-label="Toggle dark mode"
            >
              {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
            <a
              href="https://github.com/wyattowalsh/riso"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100 hover:bg-white/80 dark:hover:bg-gray-900/80 transition-colors"
              aria-label="View on GitHub"
            >
              <Github className="h-5 w-5" />
            </a>
          </div>
        </div>

        <div className="flex md:hidden items-center justify-between gap-3 pb-3">
          <a
            href="#wizard"
            className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl border border-white/70 dark:border-gray-800/70 bg-white/80 dark:bg-gray-900/70 px-3 py-2 text-xs font-semibold text-gray-700 dark:text-gray-200"
          >
            <Sparkles className="h-4 w-4" />
            Builder
          </a>
          <a
            href="/docs/"
            className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl border border-white/70 dark:border-gray-800/70 bg-white/80 dark:bg-gray-900/70 px-3 py-2 text-xs font-semibold text-gray-700 dark:text-gray-200"
          >
            <BookOpen className="h-4 w-4" />
            Docs
          </a>
        </div>
      </div>
    </header>
  )
}
