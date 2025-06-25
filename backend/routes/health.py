from fastapi import APIRouter, Request, HTTPException
import socket
import os
import time
from datetime import datetime
from pathlib import Path
import uuid
from utils.logging import log_structured_event, log_request_response

router = APIRouter()

@router.get("/health")
async def health_check(request: Request):
    """ヘルスチェックエンドポイント - OpenTelemetry対応"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # リクエスト開始ログ
    log_structured_event(
        "health_check_start",
        "Health check request received",
        level="INFO",
        request_id=request_id,
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent", "unknown"),
        method="GET",
        path="/health"
    )
    
    try:
        # システム情報を収集
        hostname = socket.gethostname()
        pod_name = os.getenv("POD_NAME", hostname)
        node_name = os.getenv("NODE_NAME", "unknown")
        environment = os.getenv("ENVIRONMENT", "development")
        
        # ASCIIアートファイルの状態確認
        ascii_dir = Path("ascii")
        ascii_files_count = 0
        ascii_files_size = 0
        
        if ascii_dir.exists():
            txt_files = list(ascii_dir.glob("*.txt"))
            ascii_files_count = len(txt_files)
            
            for file_path in txt_files:
                try:
                    ascii_files_size += file_path.stat().st_size
                except Exception:
                    pass
        
        # レスポンス時間を計算
        response_time = (time.time() - start_time) * 1000
        
        # ヘルスチェック結果
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id,
            "response_time_ms": round(response_time, 2),
            "system": {
                "hostname": hostname,
                "pod_name": pod_name,
                "node_name": node_name,
                "environment": environment,
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
            },
            "ascii_art": {
                "files_count": ascii_files_count,
                "total_size_bytes": ascii_files_size,
                "directory_exists": ascii_dir.exists()
            },
            "memory": {
                "available_mb": round(os.getloadavg()[0], 2) if hasattr(os, 'getloadavg') else 0
            }
        }
        
        # 成功ログ（レスポンス情報を含む）
        log_request_response(
            request=request,
            response_data=health_status,
            status_code=200,
            response_time_ms=response_time,
            request_id=request_id,
            ascii_files_count=ascii_files_count,
            ascii_files_size=ascii_files_size,
            health_status="healthy"
        )
        
        return health_status
        
    except Exception as e:
        # エラーログ
        error_response_time = (time.time() - start_time) * 1000
        error_detail = {
            "status": "unhealthy",
            "error": str(e),
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        log_structured_event(
            "health_check_error",
            f"Health check failed: {str(e)}",
            level="ERROR",
            request_id=request_id,
            response_time_ms=round(error_response_time, 2),
            error_type=type(e).__name__,
            error_message=str(e),
            status_code=500,
            response_data=error_detail
        )
        
        raise HTTPException(status_code=500, detail=error_detail) 
