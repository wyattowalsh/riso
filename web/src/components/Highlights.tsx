import { ShieldCheck, Wand2, Layers3 } from 'lucide-react'
import { cn } from '../lib/utils'

const HIGHLIGHTS = [
  {
    title: 'Modular',
    description: 'Enable/disable CLI, API, MCP, docs, and SaaS modules independently. Each generates its own files.',
    icon: Layers3,
    gradient: 'from-riso-grape/20 to-riso-fluorescent-pink/20',
    iconColor: 'text-riso-grape dark:text-riso-fluorescent-pink',
    accentClass: 'card-fullstack',
  },
  {
    title: 'Linting & CI included',
    description: 'Pre-configured linters, formatters, and test runners for each language. GitHub Actions workflows included.',
    icon: ShieldCheck,
    gradient: 'from-riso-green/20 to-riso-teal/20',
    iconColor: 'text-riso-green dark:text-riso-mint',
    accentClass: 'card-api',
  },
  {
    title: 'Multiple outputs',
    description: 'Copy the CLI command directly, download a copier-answers.yml, or save as a reusable preset.',
    icon: Wand2,
    gradient: 'from-riso-orange/20 to-riso-sunflower/20',
    iconColor: 'text-riso-orange dark:text-riso-apricot',
    accentClass: 'card-saas',
  },
]

export function Highlights() {
  return (
    <section className="grid gap-4 md:grid-cols-3">
      {HIGHLIGHTS.map((item, index) => (
        <div
          key={item.title}
          className={cn(
            'riso-card riso-card-accent p-6',
            'animate-fade-up hover:shadow-lg',
            item.accentClass
          )}
          style={{ animationDelay: `${index * 100}ms` }}
        >
          <div className="flex items-center gap-3">
            <div className={cn(
              'rounded-xl bg-gradient-to-br p-2.5',
              item.gradient
            )}>
              <item.icon className={cn('h-6 w-6', item.iconColor)} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{item.title}</h3>
          </div>
          <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">{item.description}</p>
        </div>
      ))}
    </section>
  )
}
