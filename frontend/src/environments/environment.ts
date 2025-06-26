// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',  // ローカル開発用
  OTLP_TRACE_EXPORTER_URL: 'http://backend:4318/v1/traces' // docker compose用
};
