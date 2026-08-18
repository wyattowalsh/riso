import { useEffect, useState } from 'react'
import { Wizard } from './components/Wizard'
import { Header } from './components/Header'
import { Presets } from './components/presets'
import { History } from './components/History'
import { Hero } from './components/Hero'
import { Highlights } from './components/Highlights'
import { DocsCallout } from './components/DocsCallout'
import { Footer } from './components/Footer'
import { SidebarSummary } from './components/SidebarSummary'
import { MobileDrawer } from './components/MobileDrawer'
import { parseShareableURL } from './lib/presets'
import { useRisoStore } from './lib/store'
import { stepAfterExternalConfigApply } from './lib/wizardGate'

function shareUrlError(href: string): string | null {
  try {
    parseShareableURL(href)
    return null
  } catch (error) {
    return error instanceof Error ? error.message : String(error)
  }
}

export default function App() {
  const { isDrawerOpen, setDrawerOpen, replaceConfig, setStep } = useRisoStore()
  const [shareError] = useState(() =>
    typeof window === 'undefined' ? null : shareUrlError(window.location.href),
  )

  useEffect(() => {
    try {
      const presetConfig = parseShareableURL(window.location.href)
      if (presetConfig) {
        replaceConfig(presetConfig)
        setStep(stepAfterExternalConfigApply(presetConfig))
      }
    } catch {
      // Share-URL parse errors are captured in shareError at first render.
    }
  }, [replaceConfig, setStep])

  return (
    <div className="min-h-screen riso-backdrop">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <Header />
      <main id="main-content" className="container mx-auto px-4 py-10 max-w-6xl space-y-10">
        <Hero />
        {shareError ? (
          <div
            role="alert"
            className="rounded-xl border border-riso-bright-red/40 bg-riso-bright-red/10 px-4 py-3 text-sm text-riso-bright-red"
          >
            Share URL rejected: {shareError}
          </div>
        ) : null}
        <Highlights />

        <section id="wizard" aria-labelledby="wizard-heading" className="space-y-6 scroll-mt-24">
          <h2 id="wizard-heading" className="sr-only">Template Configuration Wizard</h2>
          <History />
          <Presets />
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-start">
            <div className="border-t border-gray-200/70 dark:border-gray-700/60 pt-8">
              <Wizard />
            </div>
            {/* SidebarSummary: hidden on mobile (< 1024px), visible on desktop */}
            <div className="hidden lg:block">
              <SidebarSummary />
            </div>
          </div>
        </section>

        <DocsCallout />
      </main>
      <Footer />

      {/* Mobile drawer for SidebarSummary - only rendered on screens < 1024px */}
      <MobileDrawer isOpen={isDrawerOpen} onClose={() => setDrawerOpen(false)} />
    </div>
  )
}
