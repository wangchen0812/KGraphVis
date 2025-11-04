import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  define: {
    global: 'globalThis'
  },
  optimizeDeps: {
    exclude: ['neovis.js']
  },
  server: {
    // host: '0.0.0.0',
    fs: {
      allow: ['..']
    }
  },
  build: {
    rollupOptions: {
      external: ['neovis.js'],
      // 新增：处理CommonJS模块
      output: {
        globals: {
          'neovis.js': 'NeoVis'
        }
      }
    }
  }
})