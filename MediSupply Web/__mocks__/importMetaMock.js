// Mock de import.meta.env para Jest (CommonJS compatible)
Object.defineProperty(globalThis, 'import', {
  value: {
    meta: {
      env: {
        VITE_API_BASE_RUTAS_URL: 'http://localhost:8005',
        VITE_API_BASE_URL: 'http://localhost:8000'
      }
    }
  },
});
