// src/types/import-meta.d.ts
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_BASE_LOGIN_URL: string;

}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
