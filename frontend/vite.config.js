import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { rmSync } from 'node:fs'
import { resolve } from 'node:path'

function omitReferenceImages() {
  return {
    name: 'omit-reference-images',
    closeBundle() {
      rmSync(resolve(import.meta.dirname, 'dist/front-end-images'), { recursive: true, force: true });
    },
  };
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), omitReferenceImages()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor';
          }
          return undefined;
        },
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.PARVA_DEV_API_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/v3/api': {
        target: process.env.PARVA_DEV_API_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    globals: true,
    css: true,
  },
})
