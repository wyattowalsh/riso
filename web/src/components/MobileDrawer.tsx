import { useEffect, useCallback } from 'react'
import { X } from 'lucide-react'
import { cn } from '../lib/utils'
import { SidebarSummary } from './SidebarSummary'

interface MobileDrawerProps {
  isOpen: boolean
  onClose: () => void
}

export function MobileDrawer({ isOpen, onClose }: MobileDrawerProps) {
  // Handle escape key press
  const handleEscape = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose()
      }
    },
    [isOpen, onClose]
  )

  // Handle body scroll lock and escape key
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
      document.addEventListener('keydown', handleEscape)
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.body.style.overflow = ''
      document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen, handleEscape])

  if (!isOpen) {
    return null
  }

  return (
    <>
      {/* Backdrop overlay with blur */}
      <div
        className={cn(
          'fixed inset-0 z-[60] bg-black/40 backdrop-blur-sm transition-opacity duration-300 lg:hidden',
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Slide-in drawer */}
      <aside
        className={cn(
          'fixed top-0 right-0 z-[70] h-full bg-white/95 dark:bg-gray-950/95 backdrop-blur-lg',
          'w-[320px] sm:w-[380px]',
          'border-l border-gray-200/50 dark:border-gray-800/50',
          'shadow-2xl shadow-black/10 dark:shadow-black/30',
          'transition-transform duration-300 ease-out',
          'overflow-y-auto overscroll-contain',
          'lg:hidden',
          'translate-x-0'
        )}
        aria-label="Configuration summary"
        aria-hidden={!isOpen}
        role="dialog"
        aria-modal="true"
      >
        {/* Drawer header */}
        <div className="sticky top-0 z-10 flex items-center justify-between p-4 border-b border-gray-200/50 dark:border-gray-800/50 bg-white/90 dark:bg-gray-950/90 backdrop-blur-sm">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Configuration
          </h2>
          <button
            onClick={onClose}
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-xl',
              'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200',
              'hover:bg-gray-100 dark:hover:bg-gray-800',
              'transition-colors duration-200',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-riso-federal-blue focus-visible:ring-offset-2'
            )}
            aria-label="Close drawer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Drawer content */}
        <div className="p-4">
          <SidebarSummary />
        </div>
      </aside>
    </>
  )
}
