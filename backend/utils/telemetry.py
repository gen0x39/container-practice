import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

def init_telemetry():
    """OpenTelemetryの初期化"""
    # リソース属性の設定（Semantic Conventionsを使用）
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "backend-service"),
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("ENVIRONMENT", "development")
    })
    
    # トレーサープロバイダーの設定
    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    # エクスポーターの設定
    exporter_type = os.getenv("OTEL_TRACES_EXPORTER", "console")
    
    if exporter_type == "otlp":
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            exporter = OTLPSpanExporter(
                endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
            )
            print("Using OTLP exporter")
        except ImportError:
            print("Warning: opentelemetry-exporter-otlp-proto-grpc not installed, falling back to console")
            exporter = ConsoleSpanExporter()
    else:
        exporter = ConsoleSpanExporter()
        print("Using Console exporter")
    
    # スパンプロセッサーの設定
    span_processor = BatchSpanProcessor(exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # トレーサーの取得
    return trace.get_tracer(__name__)
