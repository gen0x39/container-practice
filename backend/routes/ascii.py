from fastapi import APIRouter, Request, HTTPException
import time
import uuid
import random
from datetime import datetime
from pathlib import Path
from utils.logging import log_structured_event, log_request_response

router = APIRouter()

@router.get("/ascii-all")
async def get_all_ascii_art(request: Request):
    """すべてのASCIIアートを一度に取得"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    log_structured_event(
        "ascii_all_request_start",
        "ASCII art request started",
        level="INFO",
        request_id=request_id,
        method="GET",
        path="/ascii-all"
    )
    
    try:
        ascii_dir = Path("ascii")
        if not ascii_dir.exists():
            log_structured_event(
                "ascii_all_error",
                "ASCII directory not found",
                level="WARNING",
                request_id=request_id,
                error_type="DirectoryNotFound"
            )
            return []
        
        txt_files = list(ascii_dir.glob("*.txt"))
        ascii_arts = []
        
        for i, file_path in enumerate(txt_files, 1):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                title = file_path.stem.replace('_', ' ').title()
                
                # ランダムないいね数とリツイート数を生成（実際のアプリではデータベースから取得）
                likes = random.randint(0, 2000)
                retweets = random.randint(0, 500)
                
                ascii_arts.append({
                    "tweet": content,
                    "like": likes,
                    "rt": retweets,
                    "id": i,
                    "title": title,
                    "category": "アニメ",
                    "author": "ASCIIアーティスト",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })
                
                log_structured_event(
                    "ascii_file_loaded",
                    f"ASCII file loaded successfully",
                    level="DEBUG",
                    request_id=request_id,
                    filename=file_path.name,
                    file_size=len(content),
                    file_id=i,
                    likes=likes,
                    retweets=retweets
                )
                
            except Exception as e:
                log_structured_event(
                    "ascii_file_error",
                    f"Failed to load ASCII file: {str(e)}",
                    level="ERROR",
                    request_id=request_id,
                    filename=file_path.name,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
        
        response_time = (time.time() - start_time) * 1000
        
        log_request_response(
            request=request,
            response_data=ascii_arts,
            status_code=200,
            response_time_ms=response_time,
            request_id=request_id,
            files_loaded=len(ascii_arts),
            total_files=len(txt_files)
        )
        
        return ascii_arts
        
    except Exception as e:
        error_response_time = (time.time() - start_time) * 1000
        
        log_structured_event(
            "ascii_all_request_error",
            f"ASCII art request failed: {str(e)}",
            level="ERROR",
            request_id=request_id,
            response_time_ms=round(error_response_time, 2),
            error_type=type(e).__name__,
            error_message=str(e),
            status_code=500
        )
        
        raise HTTPException(status_code=500, detail={"error": str(e)}) 
