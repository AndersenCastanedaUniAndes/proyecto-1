interface AppConfig {
  API_BASE_URL: string;
  API_BASE_LOGIN_URL:string;
}

const config: AppConfig = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  API_BASE_LOGIN_URL: import.meta.env.VITE_API_BASE_LOGIN_URL || "http://localhost:8001",
};

export default config;
