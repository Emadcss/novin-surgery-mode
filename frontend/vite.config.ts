/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// در حالت توسعه، درخواست‌های /api و /media به بک‌اند FastAPI می‌روند.
const target = process.env.VITE_DEV_API ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  clearScreen: false,
  server: { port: 5173, strictPort: true, proxy: { '/api': target, '/media': target } },
  build: { target: 'es2022', sourcemap: false },
  test: { environment: 'node' },
})
