import { resolve } from 'node:path'
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'WagtailHeraldSchema',
      fileName: (format) =>
        `js/schema-widget.${format === 'es' ? 'js' : 'iife.js'}`,
      formats: ['es', 'iife'],
    },
    outDir: resolve(__dirname, '../src/wagtail_herald/static/wagtail_herald'),
    emptyOutDir: false,
    sourcemap: true,
    minify: 'terser',
    terserOptions: {
      mangle: {
        // Avoid using $ as it conflicts with jQuery in Wagtail admin
        reserved: ['$', 'jQuery'],
        keep_classnames: true,
      },
    },
    rollupOptions: {
      output: {
        assetFileNames: (assetInfo) => {
          if (assetInfo.name?.endsWith('.css')) {
            return 'css/schema-widget.css'
          }
          return assetInfo.name ?? ''
        },
      },
    },
  },
})
