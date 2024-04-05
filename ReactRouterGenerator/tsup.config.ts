import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/cli.ts'],
  splitting: false,
  sourcemap: true,
  format: ['esm'],
  clean: true,
  outDir: 'dist',
  target: 'esnext'
})
