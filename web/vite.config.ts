import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'

const docsSource = path.resolve(__dirname, '../docs/_build')

function copyDocsPlugin() {
  return {
    name: 'copy-docs',
    closeBundle() {
      if (!fs.existsSync(docsSource)) {
        console.warn('[copy-docs] docs/_build not found, skipping docs copy.')
        return
      }
      const docsDest = path.resolve(__dirname, 'dist/docs')
      fs.rmSync(docsDest, { recursive: true, force: true })
      fs.mkdirSync(docsDest, { recursive: true })
      fs.cpSync(docsSource, docsDest, { recursive: true })
      console.log('[copy-docs] Copied docs/_build -> dist/docs')
    },
  }
}

export default defineConfig({
  plugins: [react(), copyDocsPlugin()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    open: true,
    fs: {
      allow: [path.resolve(__dirname, '..')],
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
