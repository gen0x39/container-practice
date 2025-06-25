from fastapi import APIRouter
from opentelemetry import trace
import time

router = APIRouter()
tracer = trace.get_tracer(__name__)

def child_func_level2():
    with tracer.start_as_current_span("child_func_level2_span"):
        # ここで何か処理（例：リストの合計計算をforループで実施）
        total = 0
        for i in range(100000):
            total += i
        time.sleep(0.1)  # 少しだけ処理時間を稼ぐ
        return f"child level2 result, total={total}"

def child_func_level1():
    with tracer.start_as_current_span("child_func_level1_span"):
        # ここでchild_func_level2を呼び出す
        result = child_func_level2()
        return f"child level1 result, {result}"

@router.get("/trace-nest")
def parent_endpoint():
    with tracer.start_as_current_span("parent_endpoint_span"):
        result = child_func_level1()
        return {"message": "done", "result": result} 
