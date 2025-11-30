interface AppConfig {
  API_BASE_URL: string;
  API_BASE_LOGIN_URL:string;
  API_BASE_PROVEEDORES_URL:string;
  API_BASE_VENTAS_URL:string;
  API_BASE_PLANES_URL:string;
  API_BASE_INVENTARIO_URL:string;
  API_BASE_RUTAS_URL:string;
}

const config: AppConfig = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8003",
  API_BASE_LOGIN_URL: import.meta.env.VITE_API_BASE_LOGIN_URL || "http://127.0.0.1:8001",
  API_BASE_PROVEEDORES_URL: import.meta.env.VITE_API_BASE_PROVEEDORES_URL || "http://127.0.0.1:8002",
  API_BASE_VENTAS_URL: import.meta.env.VITE_API_BASE_VENTAS_URL || "http://127.0.0.1:8004",
  API_BASE_PLANES_URL: import.meta.env.VITE_API_BASE_PLANES_URL || "http://127.0.0.1:8001",
  API_BASE_INVENTARIO_URL: import.meta.env.VITE_API_BASE_INVENTARIO_URL || "http://127.0.0.1:8005",
  API_BASE_RUTAS_URL: import.meta.env.VITE_API_BASE_RUTAS_URL || "http://127.0.0.1:8006"
  
};

export default config;
