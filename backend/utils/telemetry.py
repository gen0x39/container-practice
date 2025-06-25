from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

def init_telemetry():
    """OpenTelemetryの初期化"""
    # トレーサープロバイダーの設定
    trace.set_tracer_provider(TracerProvider())
    
    # コンソールエクスポーターの設定
    console_exporter = ConsoleSpanExporter()
    span_processor = BatchSpanProcessor(console_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # トレーサーの取得
    return trace.get_tracer(__name__) 
