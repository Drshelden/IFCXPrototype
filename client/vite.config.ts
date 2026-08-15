import { defineConfig } from 'vite';

// Proxies API/viewer-proxy traffic to the Flask dev server so `npm run dev`
// works standalone; the built output (`npm run build` -> dist/) is served
// directly by Flask in production, where these paths are same-origin anyway.
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
      '/viewer-proxy': {
        target: 'http://localhost:5000',
        ws: false,
        // SSE (/events) is a long-lived GET stream; the default proxy
        // config already passes it through unbuffered.
      },
    },
  },
  build: {
    outDir: 'dist',
  },
});
