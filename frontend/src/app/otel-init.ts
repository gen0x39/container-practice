import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { environment } from '../environments/environment';

if (typeof window !== 'undefined') {
  console.log("otel-init.ts initialized"); // ← ここを追加
  console.log(environment.OTLP_TRACE_EXPORTER_URL);

  const exporter = new OTLPTraceExporter({
    url: environment.OTLP_TRACE_EXPORTER_URL,
  });

  const provider = new WebTracerProvider({
    spanProcessors: [new BatchSpanProcessor(exporter)],
  });

  provider.register();

  registerInstrumentations({
    instrumentations: [
      new FetchInstrumentation({
        propagateTraceHeaderCorsUrls: /.*/,
      }),
    ],
  });
}
