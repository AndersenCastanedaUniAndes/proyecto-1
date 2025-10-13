// src/types/import-meta.d.ts
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  // Agrega aquí otras variables de entorno que uses
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
