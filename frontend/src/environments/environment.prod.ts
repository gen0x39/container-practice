// src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'http://backend-service.bqnq.svc.cluster.local',  // EKS内のService名
  OTLP_TRACE_EXPORTER_URL: 'http://datadog-agent.monitoring.svc.cluster.local:4318/v1/traces' // 本番用
};
