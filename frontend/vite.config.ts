/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuración dinámica según entorno
const isProduction = process.env.NODE_ENV === 'production' || process.env.VITE_ENV === 'prod'
const frontendPort = process.env.PORT ? parseInt(process.env.PORT) : (isProduction ? 5174 : 5179)
const backendPort = isProduction ? 5002 : 5000  // Backend siempre en puerto 5000

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Escuchar en todas las interfaces de red
    port: frontendPort,
    proxy: {
      '/api': {
        target: `http://localhost:${backendPort}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    },
    watch: {
      usePolling: true, // Usar polling para evitar límite de file watchers
    }
  },
  build: {
    // Code splitting & optimization
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks - librerías grandes
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'chart-vendor': ['recharts'],
          'query-vendor': ['@tanstack/react-query'],
          'ui-vendor': ['lucide-react'],
          // Socket.IO separado
          'socket-vendor': ['socket.io-client'],
        },
      },
    },
    // Optimizaciones
    target: 'es2015',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: isProduction, // Remove console.log en producción
        drop_debugger: true,
      },
    },
    // Chunk size warnings
    chunkSizeWarningLimit: 600,
    // Source maps solo en dev
    sourcemap: !isProduction,
  },
  // Optimizaciones de dependencias
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@tanstack/react-query',
      'axios',
      'socket.io-client',
    ],
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        'src/main.tsx',
        'src/vite-env.d.ts'
      ]
    }
  }
})
