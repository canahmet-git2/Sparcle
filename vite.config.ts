import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
// import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist/renderer',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html')
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    // host: 'localhost', // Temporarily commented out
    // port: 5173, // Temporarily commented out
    // strictPort: true, // Temporarily commented out
  },
}); 