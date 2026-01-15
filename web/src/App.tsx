import { Wizard } from './components/Wizard'
import { Header } from './components/Header'
import { Presets } from './components/Presets'
import { History } from './components/History'
import { Hero } from './components/Hero'
import { Highlights } from './components/Highlights'
import { DocsCallout } from './components/DocsCallout'
import { Footer } from './components/Footer'
import { SidebarSummary } from './components/SidebarSummary'

export default function App() {
  return (
    <div className="min-h-screen riso-backdrop">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <Header />
      <main id="main-content" className="container mx-auto px-4 py-10 max-w-6xl space-y-10">
        <Hero />
        <Highlights />

        <section id="wizard" aria-labelledby="wizard-heading" className="space-y-6 scroll-mt-24">
          <h2 id="wizard-heading" className="sr-only">Template Configuration Wizard</h2>
          <History />
          <Presets />
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-start">
            <div className="border-t border-gray-200/70 dark:border-gray-700/60 pt-8">
              <Wizard />
            </div>
            <SidebarSummary />
          </div>
        </section>

        <DocsCallout />
      </main>
      <Footer />
    </div>
  )
}
