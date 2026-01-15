import { ShieldCheck, Wand2, Layers3 } from 'lucide-react'

const HIGHLIGHTS = [
  {
    title: 'Quality gate included',
    description: 'Ruff, ty, pylint, pytest, coverage, and CI checks are prewired with strict profiles.',
    icon: ShieldCheck,
  },
  {
    title: 'Docs that match your stack',
    description: 'Choose Fumadocs, Docusaurus, or Shibuya Sphinx with the toggles you need.',
    icon: Layers3,
  },
  {
    title: 'One flow, many outputs',
    description: 'Generate CLI commands, download Copier answers, and save presets for later.',
    icon: Wand2,
  },
]

export function Highlights() {
  return (
    <section className="grid gap-4 md:grid-cols-3">
      {HIGHLIGHTS.map((item) => (
        <div key={item.title} className="riso-card-soft p-5 sm:p-6">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-riso-100/80 dark:bg-riso-900/40 p-2 text-riso-600 dark:text-riso-300">
              <item.icon className="h-5 w-5" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{item.title}</h3>
          </div>
          <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">{item.description}</p>
        </div>
      ))}
    </section>
  )
}
