from fastapi import APIRouter, Request, HTTPException
import json
import time
import uuid
from utils.logging import log_structured_event, log_request_response

router = APIRouter()

@router.get("/items")
async def get_items(request: Request):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    log_structured_event(
        "items_request",
        "Items endpoint accessed",
        level="INFO",
        request_id=request_id,
        method="GET",
        path="/items"
    )
    
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
        
        response_time = (time.time() - start_time) * 1000
        
        log_request_response(
            request=request,
            response_data=data,
            status_code=200,
            response_time_ms=response_time,
            request_id=request_id,
            items_count=len(data) if isinstance(data, list) else 0
        )
        
        return data
        
    except Exception as e:
        error_response_time = (time.time() - start_time) * 1000
        
        log_structured_event(
            "items_request_error",
            f"Failed to load items: {str(e)}",
            level="ERROR",
            request_id=request_id,
            response_time_ms=round(error_response_time, 2),
            error_type=type(e).__name__,
            error_message=str(e),
            status_code=500
        )
        
        raise HTTPException(status_code=500, detail={"error": str(e)}) 
