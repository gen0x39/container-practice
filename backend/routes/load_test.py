from fastapi import APIRouter
import time
import socket

router = APIRouter()

@router.get("/load-test")
def load_test(seconds: int = 10, cpu_intensive: bool = True):
    """負荷テスト用エンドポイント"""
    start_time = time.time()
    
    if cpu_intensive:
        # CPU負荷をかける処理
        end_time = start_time + seconds
        while time.time() < end_time:
            # CPU負荷をかける計算
            sum(range(10000))
    
    return {
        "message": f"負荷テスト完了: {seconds}秒間実行",
        "pod_name": socket.gethostname(),
        "execution_time": time.time() - start_time
    } 
