// src/types/import-meta.d.ts
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_BASE_LOGIN_URL: string;
  readonly VITE_API_BASE_PROVEEDORES_URL: string;
  readonly VITE_API_BASE_VENTAS_URL: string;
  readonly VITE_API_BASE_PLANES_URL: string;
  readonly VITE_API_BASE_INVENTARIO_URL: string;
  readonly VITE_API_BASE_RUTAS_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
