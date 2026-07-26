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

const apiProxy = {
  '/api': {
    target: process.env.PARVA_DEV_API_TARGET || 'http://127.0.0.1:8000',
    changeOrigin: true,
  },
  '/v3/api': {
    target: process.env.PARVA_DEV_API_TARGET || 'http://127.0.0.1:8000',
    changeOrigin: true,
  },
  '/v4/api': {
    target: process.env.PARVA_DEV_API_TARGET || 'http://127.0.0.1:8000',
    changeOrigin: true,
  },
  '/v5/api': {
    target: process.env.PARVA_DEV_API_TARGET || 'http://127.0.0.1:8000',
    changeOrigin: true,
  },
  '/health': {
    target: process.env.PARVA_DEV_API_TARGET || 'http://127.0.0.1:8000',
    changeOrigin: true,
  },
};

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
    proxy: apiProxy,
  },
  preview: {
    proxy: apiProxy,
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    globals: true,
    css: false,
  },
})
