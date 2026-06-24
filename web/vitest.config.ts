import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()] as any,
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/__tests__/setup.ts'],
    include: ['src/**/*.{test,spec}.{js,ts,jsx,tsx}'],
    testTimeout: 10000,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/__tests__/setup.ts',
        'src/__tests__/test-utils.tsx',
        '**/*.d.ts',
        '**/*.config.*',
        '**/dist/**',
        'public/**',
        'tests/e2e/**',
        'api/**',
      ],
      thresholds: {
        lines: 6,
        functions: 24,
        branches: 60,
        statements: 6,
      },
    },
  },
})
