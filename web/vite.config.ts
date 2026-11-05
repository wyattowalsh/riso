import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import fs from 'fs'

const docsSource = path.resolve(import.meta.dirname, '../docs/_build')

function copyDocsPlugin() {
  return {
    name: 'copy-docs',
    apply: 'build' as const,
    closeBundle() {
      if (!fs.existsSync(path.join(docsSource, 'index.html'))) {
        throw new Error(
          '[copy-docs] Built documentation is required. Run pnpm build to generate docs/_build first.',
        )
      }
      const docsDest = path.resolve(import.meta.dirname, 'dist/docs')
      fs.rmSync(docsDest, { recursive: true, force: true })
      fs.mkdirSync(docsDest, { recursive: true })
      fs.cpSync(docsSource, docsDest, { recursive: true })
      console.log('[copy-docs] Copied docs/_build -> dist/docs')
    },
  }
}

export default defineConfig({
  plugins: [react(), tailwindcss(), copyDocsPlugin()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    port: 5173,
    open: true,
    fs: {
      allow: [path.resolve(import.meta.dirname, '..')],
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
