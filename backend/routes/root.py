from fastapi import APIRouter, Request
import time
import uuid
from utils.logging import log_structured_event, log_request_response

router = APIRouter()

@router.get("/")
async def root(request: Request):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    log_structured_event(
        "root_access",
        "Root endpoint accessed",
        level="INFO",
        request_id=request_id,
        method="GET",
        path="/"
    )
    
    response_data = "Hello World"
    response_time = (time.time() - start_time) * 1000
    
    log_request_response(
        request=request,
        response_data=response_data,
        status_code=200,
        response_time_ms=response_time,
        request_id=request_id
    )
    
    return response_data 
