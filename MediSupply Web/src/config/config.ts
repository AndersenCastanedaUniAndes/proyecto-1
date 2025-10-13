interface AppConfig {
  API_BASE_URL: string;
}

const config: AppConfig = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
};

export default config;
