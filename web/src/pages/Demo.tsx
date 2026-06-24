/**
 * Demo Page - Live SaaS Showcase
 *
 * Interactive preview of what the Riso SaaS template produces.
 * Shows landing page, dashboard, API docs, and auth flow previews.
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  LayoutDashboard,
  FileCode,
  Lock,
  Sparkles,
  Check,
  Users,
  CreditCard,
  BarChart3,
  Settings,
  Bell,
  Search,
  Menu,
  Moon,
  Sun,
  Zap,
  Shield,
  Globe,
  Code2,
  Database,
  Rocket,
} from 'lucide-react'
import { cn } from '../lib/utils'

type DemoSection = 'landing' | 'dashboard' | 'api' | 'auth'

const DEMO_SECTIONS: { id: DemoSection; label: string; icon: React.ElementType; description: string }[] = [
  { id: 'landing', label: 'Landing Page', icon: Sparkles, description: 'Hero, features, pricing' },
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, description: 'Admin panel with analytics' },
  { id: 'api', label: 'API Docs', icon: FileCode, description: 'OpenAPI documentation' },
  { id: 'auth', label: 'Auth Flow', icon: Lock, description: 'Sign in & sign up forms' },
]

export function Demo() {
  const [activeSection, setActiveSection] = useState<DemoSection>('landing')
  const [darkMode, setDarkMode] = useState(true)

  return (
    <div className={cn('min-h-screen transition-colors duration-300', darkMode ? 'bg-gray-950' : 'bg-gray-50')}>
      {/* Demo Header */}
      <header className={cn(
        'sticky top-0 z-50 border-b backdrop-blur-lg',
        darkMode
          ? 'bg-gray-950/90 border-gray-800'
          : 'bg-white/90 border-gray-200'
      )}>
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link
                to="/"
                className={cn(
                  'flex items-center gap-2 text-sm font-medium transition-colors',
                  darkMode
                    ? 'text-gray-400 hover:text-white'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Configurator
              </Link>
              <div className={cn('h-6 w-px', darkMode ? 'bg-gray-800' : 'bg-gray-200')} />
              <div className="flex items-center gap-2">
                <div className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-lg',
                  'bg-gradient-to-br from-violet-500 to-purple-600'
                )}>
                  <Rocket className="h-4 w-4 text-white" />
                </div>
                <span className={cn('font-semibold', darkMode ? 'text-white' : 'text-gray-900')}>
                  SaaS Demo
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* Section Tabs */}
              <nav className="hidden md:flex items-center gap-1 p-1 rounded-xl bg-gray-900/50">
                {DEMO_SECTIONS.map((section) => {
                  const Icon = section.icon
                  const isActive = activeSection === section.id
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={cn(
                        'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
                        isActive
                          ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/25'
                          : darkMode
                            ? 'text-gray-400 hover:text-white hover:bg-gray-800'
                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      <span className="hidden lg:inline">{section.label}</span>
                    </button>
                  )
                })}
              </nav>

              {/* Theme Toggle */}
              <button
                onClick={() => setDarkMode(!darkMode)}
                className={cn(
                  'p-2 rounded-lg transition-colors',
                  darkMode
                    ? 'text-gray-400 hover:text-white hover:bg-gray-800'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                )}
              >
                {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Section Selector */}
      <div className="md:hidden p-4 border-b border-gray-800">
        <div className="flex gap-2 overflow-x-auto pb-2">
          {DEMO_SECTIONS.map((section) => {
            const Icon = section.icon
            const isActive = activeSection === section.id
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={cn(
                  'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all',
                  isActive
                    ? 'bg-violet-600 text-white'
                    : 'bg-gray-800 text-gray-400'
                )}
              >
                <Icon className="h-4 w-4" />
                {section.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Demo Content */}
      <main className="container mx-auto px-4 max-w-7xl py-8">
        {/* Section Info */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className={cn('text-2xl font-bold', darkMode ? 'text-white' : 'text-gray-900')}>
              {DEMO_SECTIONS.find(s => s.id === activeSection)?.label}
            </h1>
            <p className={cn('text-sm', darkMode ? 'text-gray-400' : 'text-gray-600')}>
              {DEMO_SECTIONS.find(s => s.id === activeSection)?.description}
            </p>
          </div>
          <div className={cn(
            'hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium',
            'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
          )}>
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            Live Preview
          </div>
        </div>

        {/* Preview Container */}
        <div className={cn(
          'rounded-2xl border overflow-hidden shadow-2xl',
          darkMode ? 'border-gray-800 bg-gray-900' : 'border-gray-200 bg-white'
        )}>
          {/* Browser Chrome */}
          <div className={cn(
            'flex items-center gap-3 px-4 py-3 border-b',
            darkMode ? 'bg-gray-900 border-gray-800' : 'bg-gray-50 border-gray-200'
          )}>
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
            </div>
            <div className={cn(
              'flex-1 flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm',
              darkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-100 text-gray-500'
            )}>
              <Lock className="h-3 w-3" />
              <span>demo.riso.build/{activeSection}</span>
            </div>
          </div>

          {/* Preview Content */}
          <div className="min-h-[600px]">
            {activeSection === 'landing' && <LandingPreview darkMode={darkMode} />}
            {activeSection === 'dashboard' && <DashboardPreview darkMode={darkMode} />}
            {activeSection === 'api' && <ApiDocsPreview darkMode={darkMode} />}
            {activeSection === 'auth' && <AuthPreview darkMode={darkMode} />}
          </div>
        </div>

        {/* CTA Section */}
        <div className={cn(
          'mt-8 p-6 rounded-2xl border text-center',
          darkMode ? 'bg-gray-900/50 border-gray-800' : 'bg-gray-50 border-gray-200'
        )}>
          <h2 className={cn('text-xl font-bold mb-2', darkMode ? 'text-white' : 'text-gray-900')}>
            Ready to build your own?
          </h2>
          <p className={cn('text-sm mb-4', darkMode ? 'text-gray-400' : 'text-gray-600')}>
            Use the configurator to customize your stack and generate a production-ready SaaS template.
          </p>
          <Link
            to="/#wizard"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 text-white font-semibold hover:from-violet-500 hover:to-purple-500 transition-all shadow-lg shadow-violet-500/25"
          >
            <Sparkles className="h-5 w-5" />
            Open Configurator
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </main>
    </div>
  )
}

// Landing Page Preview
function LandingPreview({ darkMode }: { darkMode: boolean }) {
  return (
    <div className={cn('overflow-y-auto max-h-[600px]', darkMode ? 'bg-gray-950' : 'bg-white')}>
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Gradient Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-violet-600/20 via-purple-600/10 to-transparent" />
        <div className="absolute top-0 right-0 w-96 h-96 bg-violet-500/30 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl" />

        <div className="relative px-8 py-20 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-sm font-medium mb-6">
            <Zap className="h-4 w-4" />
            Now with AI-powered features
          </div>
          <h1 className={cn(
            'text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-violet-200 to-purple-200 bg-clip-text text-transparent',
            !darkMode && 'from-gray-900 via-violet-600 to-purple-600'
          )}>
            Ship faster with<br />modern tooling
          </h1>
          <p className={cn('text-xl mb-8 max-w-2xl mx-auto', darkMode ? 'text-gray-400' : 'text-gray-600')}>
            A production-ready SaaS template with auth, billing, and everything you need to launch your next big idea.
          </p>
          <div className="flex items-center justify-center gap-4">
            <button className="px-6 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 text-white font-semibold hover:from-violet-500 hover:to-purple-500 transition-all shadow-lg shadow-violet-500/25">
              Get Started Free
            </button>
            <button className={cn(
              'px-6 py-3 rounded-xl font-semibold border transition-all',
              darkMode
                ? 'border-gray-700 text-gray-300 hover:bg-gray-800'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            )}>
              View Demo
            </button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className={cn('px-8 py-16', darkMode ? 'bg-gray-900/50' : 'bg-gray-50')}>
        <h2 className={cn('text-3xl font-bold text-center mb-12', darkMode ? 'text-white' : 'text-gray-900')}>
          Everything you need
        </h2>
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {[
            { icon: Shield, title: 'Authentication', desc: 'Clerk, Auth.js, or Lucia' },
            { icon: CreditCard, title: 'Payments', desc: 'Stripe, Paddle, LemonSqueezy' },
            { icon: Database, title: 'Database', desc: 'Neon or Supabase Postgres' },
            { icon: Globe, title: 'Hosting', desc: 'Vercel or Cloudflare' },
            { icon: BarChart3, title: 'Analytics', desc: 'PostHog or Amplitude' },
            { icon: Code2, title: 'API', desc: 'REST, GraphQL, WebSocket' },
          ].map((feature, i) => (
            <div
              key={i}
              className={cn(
                'p-6 rounded-xl border transition-all hover:scale-105',
                darkMode
                  ? 'bg-gray-800/50 border-gray-700 hover:border-violet-500/50'
                  : 'bg-white border-gray-200 hover:border-violet-300'
              )}
            >
              <feature.icon className={cn('h-8 w-8 mb-4', darkMode ? 'text-violet-400' : 'text-violet-600')} />
              <h3 className={cn('font-semibold mb-2', darkMode ? 'text-white' : 'text-gray-900')}>
                {feature.title}
              </h3>
              <p className={cn('text-sm', darkMode ? 'text-gray-400' : 'text-gray-600')}>
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Pricing Section */}
      <div className="px-8 py-16">
        <h2 className={cn('text-3xl font-bold text-center mb-4', darkMode ? 'text-white' : 'text-gray-900')}>
          Simple pricing
        </h2>
        <p className={cn('text-center mb-12', darkMode ? 'text-gray-400' : 'text-gray-600')}>
          Choose the plan that's right for you
        </p>
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {[
            { name: 'Starter', price: '$9', features: ['5 projects', '10GB storage', 'Email support'] },
            { name: 'Pro', price: '$29', features: ['Unlimited projects', '100GB storage', 'Priority support', 'Custom domain'], popular: true },
            { name: 'Enterprise', price: '$99', features: ['Everything in Pro', 'SSO', 'SLA', 'Dedicated support'] },
          ].map((plan, i) => (
            <div
              key={i}
              className={cn(
                'relative p-6 rounded-xl border',
                plan.popular
                  ? 'bg-gradient-to-b from-violet-600/20 to-transparent border-violet-500/50 ring-2 ring-violet-500/20'
                  : darkMode
                    ? 'bg-gray-800/50 border-gray-700'
                    : 'bg-white border-gray-200'
              )}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-violet-600 text-white text-xs font-medium">
                  Most Popular
                </div>
              )}
              <h3 className={cn('text-lg font-semibold mb-2', darkMode ? 'text-white' : 'text-gray-900')}>
                {plan.name}
              </h3>
              <div className="mb-4">
                <span className={cn('text-4xl font-bold', darkMode ? 'text-white' : 'text-gray-900')}>
                  {plan.price}
                </span>
                <span className={cn('text-sm', darkMode ? 'text-gray-400' : 'text-gray-600')}>/month</span>
              </div>
              <ul className="space-y-2 mb-6">
                {plan.features.map((feature, j) => (
                  <li key={j} className="flex items-center gap-2 text-sm">
                    <Check className={cn('h-4 w-4', darkMode ? 'text-violet-400' : 'text-violet-600')} />
                    <span className={darkMode ? 'text-gray-300' : 'text-gray-700'}>{feature}</span>
                  </li>
                ))}
              </ul>
              <button className={cn(
                'w-full py-2 rounded-lg font-medium transition-all',
                plan.popular
                  ? 'bg-violet-600 text-white hover:bg-violet-500'
                  : darkMode
                    ? 'bg-gray-700 text-white hover:bg-gray-600'
                    : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
              )}>
                Get Started
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Dashboard Preview
function DashboardPreview({ darkMode }: { darkMode: boolean }) {
  return (
    <div className={cn('flex h-[600px]', darkMode ? 'bg-gray-950' : 'bg-gray-100')}>
      {/* Sidebar */}
      <aside className={cn(
        'w-64 border-r flex-shrink-0',
        darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'
      )}>
        <div className="p-4">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <Rocket className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className={cn('font-semibold', darkMode ? 'text-white' : 'text-gray-900')}>Acme Inc</div>
              <div className={cn('text-xs', darkMode ? 'text-gray-500' : 'text-gray-500')}>Pro Plan</div>
            </div>
          </div>

          <nav className="space-y-1">
            {[
              { icon: LayoutDashboard, label: 'Dashboard', active: true },
              { icon: Users, label: 'Customers' },
              { icon: CreditCard, label: 'Billing' },
              { icon: BarChart3, label: 'Analytics' },
              { icon: Settings, label: 'Settings' },
            ].map((item, i) => (
              <button
                key={i}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all',
                  item.active
                    ? 'bg-violet-600 text-white'
                    : darkMode
                      ? 'text-gray-400 hover:text-white hover:bg-gray-800'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                )}
              >
                <item.icon className="h-5 w-5" />
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* Top Bar */}
        <div className={cn(
          'sticky top-0 flex items-center justify-between px-6 py-4 border-b',
          darkMode ? 'bg-gray-950/90 border-gray-800' : 'bg-white/90 border-gray-200'
        )}>
          <div className="flex items-center gap-4">
            <button className={cn('p-2 rounded-lg', darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-100')}>
              <Menu className={cn('h-5 w-5', darkMode ? 'text-gray-400' : 'text-gray-600')} />
            </button>
            <div className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-lg',
              darkMode ? 'bg-gray-800' : 'bg-gray-100'
            )}>
              <Search className={cn('h-4 w-4', darkMode ? 'text-gray-500' : 'text-gray-400')} />
              <span className={cn('text-sm', darkMode ? 'text-gray-500' : 'text-gray-400')}>Search...</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button className={cn('p-2 rounded-lg relative', darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-100')}>
              <Bell className={cn('h-5 w-5', darkMode ? 'text-gray-400' : 'text-gray-600')} />
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-red-500" />
            </button>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600" />
          </div>
        </div>

        {/* Dashboard Content */}
        <div className="p-6 space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Total Revenue', value: '$45,231', change: '+20.1%', up: true },
              { label: 'Subscriptions', value: '2,350', change: '+12.5%', up: true },
              { label: 'Active Users', value: '12.4K', change: '+8.2%', up: true },
              { label: 'Churn Rate', value: '2.1%', change: '-0.4%', up: false },
            ].map((stat, i) => (
              <div
                key={i}
                className={cn(
                  'p-4 rounded-xl border',
                  darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'
                )}
              >
                <div className={cn('text-sm mb-1', darkMode ? 'text-gray-400' : 'text-gray-600')}>
                  {stat.label}
                </div>
                <div className="flex items-end justify-between">
                  <span className={cn('text-2xl font-bold', darkMode ? 'text-white' : 'text-gray-900')}>
                    {stat.value}
                  </span>
                  <span className={cn(
                    'text-xs font-medium',
                    stat.up ? 'text-emerald-500' : 'text-red-500'
                  )}>
                    {stat.change}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Chart Placeholder */}
          <div className={cn(
            'p-6 rounded-xl border',
            darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'
          )}>
            <div className="flex items-center justify-between mb-6">
              <h3 className={cn('font-semibold', darkMode ? 'text-white' : 'text-gray-900')}>
                Revenue Overview
              </h3>
              <div className="flex gap-2">
                {['7d', '30d', '90d', '1y'].map((period, i) => (
                  <button
                    key={i}
                    className={cn(
                      'px-3 py-1 rounded-lg text-xs font-medium transition-all',
                      i === 1
                        ? 'bg-violet-600 text-white'
                        : darkMode
                          ? 'text-gray-400 hover:text-white hover:bg-gray-800'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    )}
                  >
                    {period}
                  </button>
                ))}
              </div>
            </div>
            {/* Simulated Chart */}
            <div className="h-48 flex items-end justify-between gap-2">
              {[40, 65, 45, 80, 55, 90, 70, 85, 60, 75, 95, 80].map((height, i) => (
                <div
                  key={i}
                  className="flex-1 rounded-t-lg bg-gradient-to-t from-violet-600 to-purple-500 opacity-80 hover:opacity-100 transition-opacity"
                  style={{ height: `${height}%` }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// API Docs Preview
function ApiDocsPreview({ darkMode }: { darkMode: boolean }) {
  return (
    <div className={cn('flex h-[600px]', darkMode ? 'bg-gray-950' : 'bg-white')}>
      {/* Sidebar */}
      <aside className={cn(
        'w-64 border-r overflow-auto flex-shrink-0',
        darkMode ? 'bg-gray-900 border-gray-800' : 'bg-gray-50 border-gray-200'
      )}>
        <div className="p-4">
          <div className="flex items-center gap-2 mb-6">
            <Code2 className={cn('h-5 w-5', darkMode ? 'text-violet-400' : 'text-violet-600')} />
            <span className={cn('font-semibold', darkMode ? 'text-white' : 'text-gray-900')}>API Reference</span>
          </div>

          <div className="space-y-4">
            {[
              { title: 'Authentication', endpoints: ['POST /auth/login', 'POST /auth/register', 'POST /auth/logout'] },
              { title: 'Users', endpoints: ['GET /users', 'GET /users/:id', 'PATCH /users/:id'] },
              { title: 'Subscriptions', endpoints: ['GET /subscriptions', 'POST /subscriptions', 'DELETE /subscriptions/:id'] },
            ].map((section, i) => (
              <div key={i}>
                <h4 className={cn('text-xs font-semibold uppercase tracking-wider mb-2', darkMode ? 'text-gray-500' : 'text-gray-400')}>
                  {section.title}
                </h4>
                <div className="space-y-1">
                  {section.endpoints.map((endpoint, j) => {
                    const [method, path] = endpoint.split(' ')
                    return (
                      <button
                        key={j}
                        className={cn(
                          'w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm text-left transition-all',
                          i === 0 && j === 0
                            ? darkMode ? 'bg-gray-800' : 'bg-white'
                            : darkMode
                              ? 'hover:bg-gray-800'
                              : 'hover:bg-white'
                        )}
                      >
                        <span className={cn(
                          'text-xs font-mono font-medium px-1.5 py-0.5 rounded',
                          method === 'GET' ? 'bg-emerald-500/20 text-emerald-400' :
                          method === 'POST' ? 'bg-blue-500/20 text-blue-400' :
                          method === 'PATCH' ? 'bg-amber-500/20 text-amber-400' :
                          'bg-red-500/20 text-red-400'
                        )}>
                          {method}
                        </span>
                        <span className={cn('font-mono text-xs', darkMode ? 'text-gray-300' : 'text-gray-700')}>
                          {path}
                        </span>
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-8">
        <div className="max-w-3xl">
          <div className="flex items-center gap-3 mb-6">
            <span className="px-2 py-1 rounded bg-blue-500/20 text-blue-400 text-xs font-mono font-medium">POST</span>
            <code className={cn('font-mono', darkMode ? 'text-white' : 'text-gray-900')}>/auth/login</code>
          </div>

          <h1 className={cn('text-2xl font-bold mb-4', darkMode ? 'text-white' : 'text-gray-900')}>
            User Login
          </h1>
          <p className={cn('mb-6', darkMode ? 'text-gray-400' : 'text-gray-600')}>
            Authenticate a user and receive an access token for subsequent API requests.
          </p>

          {/* Request Body */}
          <div className="mb-6">
            <h3 className={cn('text-sm font-semibold mb-3', darkMode ? 'text-white' : 'text-gray-900')}>
              Request Body
            </h3>
            <div className={cn(
              'rounded-lg overflow-hidden border',
              darkMode ? 'bg-gray-900 border-gray-800' : 'bg-gray-50 border-gray-200'
            )}>
              <pre className="p-4 text-sm font-mono overflow-x-auto">
                <code className={darkMode ? 'text-gray-300' : 'text-gray-700'}>
{`{
  "email": "user@example.com",
  "password": "secure_password"
}`}
                </code>
              </pre>
            </div>
          </div>

          {/* Response */}
          <div>
            <h3 className={cn('text-sm font-semibold mb-3', darkMode ? 'text-white' : 'text-gray-900')}>
              Response
            </h3>
            <div className={cn(
              'rounded-lg overflow-hidden border',
              darkMode ? 'bg-gray-900 border-gray-800' : 'bg-gray-50 border-gray-200'
            )}>
              <div className={cn(
                'flex items-center gap-2 px-4 py-2 border-b text-xs',
                darkMode ? 'bg-gray-800/50 border-gray-800' : 'bg-gray-100 border-gray-200'
              )}>
                <span className="text-emerald-400 font-medium">200</span>
                <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Success</span>
              </div>
              <pre className="p-4 text-sm font-mono overflow-x-auto">
                <code className={darkMode ? 'text-gray-300' : 'text-gray-700'}>
{`{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "usr_123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}`}
                </code>
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Auth Preview
function AuthPreview({ darkMode }: { darkMode: boolean }) {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin')

  return (
    <div className={cn(
      'h-[600px] flex items-center justify-center',
      darkMode
        ? 'bg-gradient-to-br from-gray-950 via-violet-950/20 to-gray-950'
        : 'bg-gradient-to-br from-gray-50 via-violet-50 to-gray-50'
    )}>
      <div className={cn(
        'w-full max-w-md p-8 rounded-2xl border shadow-2xl',
        darkMode
          ? 'bg-gray-900/80 border-gray-800 backdrop-blur-xl'
          : 'bg-white/80 border-gray-200 backdrop-blur-xl'
      )}>
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
            <Rocket className="h-5 w-5 text-white" />
          </div>
          <span className={cn('text-xl font-bold', darkMode ? 'text-white' : 'text-gray-900')}>Acme</span>
        </div>

        {/* Tabs */}
        <div className={cn(
          'flex gap-1 p-1 rounded-xl mb-6',
          darkMode ? 'bg-gray-800' : 'bg-gray-100'
        )}>
          {[
            { id: 'signin' as const, label: 'Sign In' },
            { id: 'signup' as const, label: 'Sign Up' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setMode(tab.id)}
              className={cn(
                'flex-1 py-2 rounded-lg text-sm font-medium transition-all',
                mode === tab.id
                  ? 'bg-violet-600 text-white shadow'
                  : darkMode
                    ? 'text-gray-400 hover:text-white'
                    : 'text-gray-600 hover:text-gray-900'
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Form */}
        <div className="space-y-4">
          {mode === 'signup' && (
            <div>
              <label className={cn('block text-sm font-medium mb-1.5', darkMode ? 'text-gray-300' : 'text-gray-700')}>
                Full Name
              </label>
              <input
                type="text"
                placeholder="John Doe"
                className={cn(
                  'w-full px-4 py-2.5 rounded-lg border text-sm transition-all',
                  darkMode
                    ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-violet-500'
                    : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:border-violet-500'
                )}
              />
            </div>
          )}
          <div>
            <label className={cn('block text-sm font-medium mb-1.5', darkMode ? 'text-gray-300' : 'text-gray-700')}>
              Email
            </label>
            <input
              type="email"
              placeholder="you@example.com"
              className={cn(
                'w-full px-4 py-2.5 rounded-lg border text-sm transition-all',
                darkMode
                  ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-violet-500'
                  : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:border-violet-500'
              )}
            />
          </div>
          <div>
            <label className={cn('block text-sm font-medium mb-1.5', darkMode ? 'text-gray-300' : 'text-gray-700')}>
              Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              className={cn(
                'w-full px-4 py-2.5 rounded-lg border text-sm transition-all',
                darkMode
                  ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-violet-500'
                  : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:border-violet-500'
              )}
            />
          </div>

          {mode === 'signin' && (
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded border-gray-600" />
                <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Remember me</span>
              </label>
              <a href="#" className="text-violet-400 hover:text-violet-300">Forgot password?</a>
            </div>
          )}

          <button className="w-full py-2.5 rounded-lg bg-gradient-to-r from-violet-600 to-purple-600 text-white font-semibold hover:from-violet-500 hover:to-purple-500 transition-all shadow-lg shadow-violet-500/25">
            {mode === 'signin' ? 'Sign In' : 'Create Account'}
          </button>

          <div className="relative my-6">
            <div className={cn('absolute inset-0 flex items-center', darkMode ? 'border-gray-800' : 'border-gray-200')}>
              <div className={cn('w-full border-t', darkMode ? 'border-gray-800' : 'border-gray-200')} />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className={cn('px-2', darkMode ? 'bg-gray-900 text-gray-500' : 'bg-white text-gray-500')}>
                Or continue with
              </span>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {['Google', 'GitHub', 'Apple'].map((provider) => (
              <button
                key={provider}
                className={cn(
                  'py-2.5 rounded-lg border text-sm font-medium transition-all',
                  darkMode
                    ? 'bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700'
                    : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                )}
              >
                {provider}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
