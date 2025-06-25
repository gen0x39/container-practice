import json
import logging
from datetime import datetime
import uuid
from typing import Any
from fastapi import Request

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_structured_event(event_type: str, message: str, level: str = "INFO", **kwargs):
    """OpenTelemetry対応の構造化ログ出力"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "event_type": event_type,
        "message": message,
        "service": "ascii-twitter-backend",
        "version": "1.0.0",
        "trace_id": str(uuid.uuid4()),
        "span_id": str(uuid.uuid4())[:16],
        **kwargs
    }
    
    # 標準出力にJSON形式で出力
    print(json.dumps(log_entry, ensure_ascii=False))
    
    # 通常のログも出力
    log_level = getattr(logger, level.lower(), logger.info)
    log_level(f"{event_type}: {message}")

def log_request_response(request: Request, response_data: Any, status_code: int, 
                       response_time_ms: float, request_id: str, **kwargs):
    """リクエスト・レスポンス情報を含むログ出力"""
    log_structured_event(
        "request_response",
        f"Request completed: {request.method} {request.url.path}",
        level="INFO",
        request_id=request_id,
        method=request.method,
        path=str(request.url.path),
        query_params=dict(request.query_params),
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent", "unknown"),
        status_code=status_code,
        response_time_ms=round(response_time_ms, 2),
        response_size_bytes=len(json.dumps(response_data, ensure_ascii=False)) if response_data else 0,
        response_data_type=type(response_data).__name__,
        **kwargs
    ) 
