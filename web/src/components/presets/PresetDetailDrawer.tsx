import { X, Folder, File, ChevronRight, Check, Sparkles, Clock, Layers } from 'lucide-react'
import { cn } from '../../lib/utils'
import { ICON_GRADIENTS, ICON_TEXT, type Preset, type FileTreeNode, type Complexity } from './types'

interface PresetDetailDrawerProps {
  preset: Preset | null
  isOpen: boolean
  onClose: () => void
  onApply: (preset: Preset) => void
  isSelected: boolean
}

const complexityConfig: Record<Complexity, { label: string; color: string; description: string }> = {
  beginner: {
    label: 'Beginner',
    color: 'bg-riso-green/20 text-riso-green',
    description: 'Simple setup, few moving parts',
  },
  intermediate: {
    label: 'Intermediate',
    color: 'bg-riso-sunflower/20 text-riso-orange',
    description: 'Multiple components, some complexity',
  },
  advanced: {
    label: 'Advanced',
    color: 'bg-riso-fluorescent-pink/20 text-riso-fluorescent-pink',
    description: 'Complex setup, multiple languages/services',
  },
}

function FileTreeItem({ node, depth = 0 }: { node: FileTreeNode; depth?: number }) {
  const isFolder = node.type === 'folder'
  const Icon = isFolder ? Folder : File

  return (
    <div>
      <div
        className={cn(
          'flex items-center gap-1.5 py-0.5 text-xs',
          depth > 0 && 'ml-4'
        )}
      >
        <Icon
          className={cn(
            'h-3.5 w-3.5 flex-shrink-0',
            isFolder ? 'text-riso-sunflower' : 'text-gray-400'
          )}
        />
        <span className={cn(
          isFolder ? 'text-gray-900 dark:text-white font-medium' : 'text-gray-600 dark:text-gray-400'
        )}>
          {node.name}
        </span>
        {node.description && (
          <span className="text-gray-400 dark:text-gray-500 text-[10px]">
            — {node.description}
          </span>
        )}
      </div>
      {node.children && (
        <div className="border-l border-gray-200 dark:border-gray-700 ml-1.5">
          {node.children.map((child, i) => (
            <FileTreeItem key={`${child.name}-${i}`} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  )
}

export function PresetDetailDrawer({
  preset,
  isOpen,
  onClose,
  onApply,
  isSelected,
}: PresetDetailDrawerProps) {
  if (!preset) return null

  const complexity = complexityConfig[preset.complexity]

  return (
    <>
      {/* Backdrop */}
      <div
        className={cn(
          'fixed inset-0 bg-black/40 backdrop-blur-sm z-40 transition-opacity duration-300',
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
        onClick={onClose}
      />

      {/* Drawer */}
      <div
        className={cn(
          'fixed right-0 top-0 h-full w-full max-w-lg bg-white dark:bg-gray-900 shadow-2xl z-50',
          'transform transition-transform duration-300 ease-out',
          'overflow-y-auto',
          isOpen ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm border-b border-gray-200 dark:border-gray-800 p-4 z-10">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div
                className={cn(
                  'p-2.5 rounded-xl bg-gradient-to-br',
                  ICON_GRADIENTS[preset.id]
                )}
              >
                <div className={cn(ICON_TEXT[preset.id])}>{preset.icon}</div>
              </div>
              <div>
                <h2 className="font-semibold text-lg text-gray-900 dark:text-white">
                  {preset.name}
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {preset.description}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Close"
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>

          {/* Quick stats bar */}
          <div className="mt-4 flex items-center gap-3 text-xs">
            <div className={cn('px-2 py-1 rounded-full font-medium', complexity.color)}>
              {complexity.label}
            </div>
            <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400">
              <File className="h-3.5 w-3.5" />
              ~{preset.estimatedFiles} files
            </div>
            <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400">
              <Layers className="h-3.5 w-3.5" />
              {preset.config.project_layout === 'monorepo' ? 'Monorepo' : 'Single Package'}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 space-y-6">
          {/* Purpose */}
          <section>
            <h3 className="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-semibold mb-2">
              What This Preset Does
            </h3>
            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
              {preset.purpose}
            </p>
          </section>

          {/* Use When */}
          <section>
            <h3 className="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-semibold mb-2">
              Choose This When You're
            </h3>
            <ul className="space-y-1.5">
              {preset.useWhen.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                  <ChevronRight className="h-4 w-4 text-riso-green flex-shrink-0 mt-0.5" />
                  {item}
                </li>
              ))}
            </ul>
          </section>

          {/* Tech Stack */}
          <section>
            <h3 className="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-semibold mb-2">
              Tech Stack
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {preset.techStack.map((tech) => (
                <span
                  key={tech}
                  className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs font-medium text-gray-700 dark:text-gray-300"
                >
                  {tech}
                </span>
              ))}
            </div>
          </section>

          {/* Tags */}
          <section>
            <h3 className="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-semibold mb-2">
              Categories
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {preset.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 bg-riso-federal-blue/10 dark:bg-riso-cornflower/10 text-riso-federal-blue dark:text-riso-cornflower rounded text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          </section>

          {/* File Tree Preview */}
          <section>
            <h3 className="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-semibold mb-2">
              Project Structure
            </h3>
            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 font-mono">
              {preset.fileTree.map((node, i) => (
                <FileTreeItem key={`${node.name}-${i}`} node={node} />
              ))}
            </div>
            <p className="mt-2 text-[10px] text-gray-400 dark:text-gray-500">
              * Simplified preview. Actual output includes additional config files.
            </p>
          </section>

          {/* Complexity note */}
          <section className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3">
            <div className="flex items-start gap-2">
              <Clock className="h-4 w-4 text-gray-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-medium text-gray-700 dark:text-gray-300">
                  Complexity: {complexity.label}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {complexity.description}
                </p>
              </div>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm border-t border-gray-200 dark:border-gray-800 p-4">
          <button
            onClick={() => onApply(preset)}
            className={cn(
              'w-full py-3 px-4 rounded-xl font-medium text-sm transition-all',
              'flex items-center justify-center gap-2',
              isSelected
                ? 'bg-riso-green text-white'
                : 'bg-riso-federal-blue text-white hover:bg-riso-federal-blue/90'
            )}
          >
            {isSelected ? (
              <>
                <Check className="h-4 w-4" />
                Currently Applied
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Apply This Preset
              </>
            )}
          </button>
        </div>
      </div>
    </>
  )
}
