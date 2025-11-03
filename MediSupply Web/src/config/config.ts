interface AppConfig {
  API_BASE_URL: string;
  API_BASE_LOGIN_URL:string;
  API_BASE_PROVEEDORES_URL:string;
  API_BASE_VENTAS_URL:string;
}

const config: AppConfig = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://34.170.115.55:8000",
  API_BASE_LOGIN_URL: import.meta.env.VITE_API_BASE_LOGIN_URL || "http://34.170.115.55:8001",
  API_BASE_PROVEEDORES_URL: import.meta.env.VITE_API_BASE_PROVEEDORES_URL || "http://34.170.115.55:8003",
  API_BASE_VENTAS_URL: import.meta.env.VITE_API_BASE_VENTAS_URL || "http://34.170.115.55:8004"
  
};

export default config;
