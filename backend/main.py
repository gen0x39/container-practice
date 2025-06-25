from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# ユーティリティのインポート
from utils.telemetry import init_telemetry

# ルーターのインポート
from routes import (
    health_router,
    root_router,
    items_router,
    ascii_router,
    frontend_info_router,
    load_test_router,
    tweets_router,
    upload_router,
    trace_example_router
)

# OpenTelemetryの初期化
tracer = init_telemetry()

# FastAPIアプリケーションの作成
app = FastAPI(
    title="ASCII Twitter Backend",
    description="ASCIIアートを投稿できるTwitterライクなAPI",
    version="1.0.0"
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenTelemetry FastAPI Instrumentationの設定
FastAPIInstrumentor.instrument_app(app)

# ルーターの登録
app.include_router(health_router)
app.include_router(root_router)
app.include_router(items_router)
app.include_router(ascii_router)
app.include_router(frontend_info_router)
app.include_router(load_test_router)
app.include_router(tweets_router)
app.include_router(upload_router)
app.include_router(trace_example_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
