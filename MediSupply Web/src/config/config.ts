interface AppConfig {
  API_BASE_URL: string;
  API_BASE_LOGIN_URL:string;
  API_BASE_PROVEEDORES_URL:string;
  API_BASE_VENTAS_URL:string;
  API_BASE_PLANES_URL:string;
}

const config: AppConfig = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  API_BASE_LOGIN_URL: import.meta.env.VITE_API_BASE_LOGIN_URL || "http://127.0.0.1:8001",
  API_BASE_PROVEEDORES_URL: import.meta.env.VITE_API_BASE_PROVEEDORES_URL || "http://127.0.0.1:8003",
  API_BASE_VENTAS_URL: import.meta.env.VITE_API_BASE_VENTAS_URL || "http://127.0.0.1:8004",
  API_BASE_PLANES_URL: import.meta.env.VITE_API_BASE_PLANES_URL || "http://127.0.0.1:8001"
  
};

export default config;
