from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
import json
import time
import uuid
import random
from datetime import datetime
from pathlib import Path
from models.tweet import TweetRequest
from utils.logging import log_structured_event, log_request_response
from opentelemetry import trace

router = APIRouter()

@router.get("/tweets")
async def get_all_tweets(request: Request):
    """tweetディレクトリから全てのツイートを取得"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    log_structured_event(
        "tweets_request_start",
        "Tweets request started",
        level="INFO",
        request_id=request_id,
        method="GET",
        path="/tweets"
    )
    
    try:
        tracer = trace.get_tracer(__name__)
        
        # メインのget_all_tweetsスパンを作成
        with tracer.start_as_current_span("get_all_tweets") as main_span:
            main_span.set_attribute("operation.type", "tweet_retrieval")
            main_span.set_attribute("request.id", request_id)
            
            # ファイル読み込み処理を子スパンとして作成
            with tracer.start_as_current_span("load_tweet_files") as file_span:
                file_span.set_attribute("operation.type", "file_loading")
                
                tweet_dir = Path("tweet")
                if not tweet_dir.exists():
                    file_span.set_attribute("error.type", "DirectoryNotFound")
                    log_structured_event(
                        "tweets_error",
                        "Tweet directory not found",
                        level="WARNING",
                        request_id=request_id,
                        error_type="DirectoryNotFound"
                    )
                    return []
                
                json_files = list(tweet_dir.glob("*.json"))
                file_span.set_attribute("files.found", len(json_files))
                
                tweets = []
                
                for file_path in json_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            tweet_data = json.load(f)
                        
                        tweets.append(tweet_data)
                        
                        log_structured_event(
                            "tweet_file_loaded",
                            f"Tweet JSON file loaded successfully",
                            level="DEBUG",
                            request_id=request_id,
                            filename=file_path.name,
                            tweet_id=tweet_data.get("id", "unknown")
                        )
                        
                    except Exception as e:
                        log_structured_event(
                            "tweet_file_error",
                            f"Failed to load tweet file: {str(e)}",
                            level="ERROR",
                            request_id=request_id,
                            filename=file_path.name,
                            error_type=type(e).__name__,
                            error_message=str(e)
                        )
                
                file_span.set_attribute("files.loaded", len(tweets))
            
            # ソート処理を子スパンとして作成
            with tracer.start_as_current_span("sort_tweets") as sort_span:
                sort_span.set_attribute("operation.type", "data_sorting")
                sort_span.set_attribute("tweets.to_sort", len(tweets))
                
                # タイムスタンプでソート（新しい順）
                tweets.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                
                sort_span.set_attribute("tweets.sorted", len(tweets))
            
            # メインスパンに最終結果を追加
            main_span.set_attribute("tweets.total_returned", len(tweets))
            main_span.set_attribute("operation.status", "completed")
        
        response_time = (time.time() - start_time) * 1000
        
        log_request_response(
            request=request,
            response_data=tweets,
            status_code=200,
            response_time_ms=response_time,
            request_id=request_id,
            tweets_loaded=len(tweets),
            total_files=len(json_files)
        )
        
        return tweets
        
    except Exception as e:
        error_response_time = (time.time() - start_time) * 1000
        
        log_structured_event(
            "tweets_request_error",
            f"Tweets request failed: {str(e)}",
            level="ERROR",
            request_id=request_id,
            response_time_ms=round(error_response_time, 2),
            error_type=type(e).__name__,
            error_message=str(e),
            status_code=500
        )
        
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/tweet")
async def broken_tweet(request: Request):
    """意図的に失敗するエンドポイント - バグ検出用"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # エラー検出のためのテレメトリ情報を記録
    log_structured_event(
        "bug_detected",
        "Intentional error endpoint called - potential bug in frontend",
        level="ERROR",
        request_id=request_id,
        method="POST",
        path="/tweet",
        error_type="intentional_error",
        bug_category="frontend_api_endpoint_mismatch",
        expected_endpoint="/tweet",
        actual_endpoint="/tweet",
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent", "unknown"),
        request_headers=dict(request.headers),
        timestamp=datetime.utcnow().isoformat() + "Z",
        status_code=404,
        http_status_code=404
    )
    
    # OpenTelemetryトレースでエラーを記録
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("broken_tweet_endpoint") as span:
        span.set_attribute("operation.type", "intentional_error")
        span.set_attribute("error.type", "frontend_bug")
        span.set_attribute("expected.endpoint", "/tweet")
        span.set_attribute("actual.endpoint", "/tweet")
        span.set_attribute("bug.severity", "high")
        span.set_attribute("bug.category", "api_endpoint_mismatch")
        span.record_exception(Exception("Frontend is calling wrong endpoint"))
        span.set_status(trace.Status(trace.StatusCode.ERROR, "Intentional error for bug detection"))
    
    # Datadog用の追加メトリクス
    log_structured_event(
        "datadog_metric",
        "Bug detection metric",
        level="INFO",
        metric_name="frontend.bug.detected",
        metric_value=1,
        metric_type="counter",
        tags=["bug_type:api_endpoint_mismatch", "severity:high", "service:ascii-twitter-backend"]
    )
    
    raise HTTPException(
        status_code=404,
        detail={
            "error": "Not Found: This endpoint does not exist.",
            "bug_info": {
                "type": "frontend_api_endpoint_mismatch",
                "expected": "/tweet",
                "actual": "/tweet",
                "detected_at": datetime.utcnow().isoformat() + "Z"
            }
        }
    )

@router.post("/tweet")
async def create_tweet(request: Request, tweet_data: TweetRequest):
    """ツイートを投稿してテキストファイルに保存"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    log_structured_event(
        "tweet_post_start",
        "Tweet post request started",
        level="INFO",
        request_id=request_id,
        method="POST",
        path="/tweet",
        author=tweet_data.author,
        content_length=len(tweet_data.content),
        has_ascii=tweet_data.ascii_content is not None
    )
    
    try:
        # asciiディレクトリの作成（存在しない場合）
        ascii_dir = Path("ascii")
        try:
            ascii_dir.mkdir(exist_ok=True, mode=0o755)
        except PermissionError:
            # 権限エラーの場合は/tmpディレクトリを使用
            ascii_dir = Path("/tmp/ascii")
            ascii_dir.mkdir(exist_ok=True, mode=0o755)
        
        # tweetディレクトリの作成（存在しない場合）
        tweet_dir = Path("tweet")
        try:
            tweet_dir.mkdir(exist_ok=True, mode=0o755)
        except PermissionError:
            # 権限エラーの場合は/tmpディレクトリを使用
            tweet_dir = Path("/tmp/tweet")
            tweet_dir.mkdir(exist_ok=True, mode=0o755)
        
        # ツイートIDを生成
        tweet_id = str(uuid.uuid4())
        filename = f"tweet_{tweet_id}.txt"
        file_path = ascii_dir / filename
        
        # アスキーアートが含まれている場合は保存
        ascii_path = None
        tweet_body = tweet_data.content
        
        if tweet_data.ascii_content:
            # アスキーアートをファイルに保存
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(tweet_data.ascii_content)
            ascii_path = f"ascii/{filename}"
            tweet_body = tweet_data.content + "\n" + tweet_data.ascii_content
            
            log_structured_event(
                "ascii_saved",
                "ASCII art saved to file",
                level="INFO",
                request_id=request_id,
                ascii_path=ascii_path,
                ascii_length=len(tweet_data.ascii_content)
            )
        
        # レスポンス用のツイートオブジェクトを作成
        tweet_response = {
            "tweet": tweet_body,  # テキスト＋アスキーアート
            "like": random.randint(5000, 100000),
            "rt": random.randint(500, 50000),
            "id": tweet_id,
            "title": "新規ツイート",
            "category": tweet_data.category,
            "author": tweet_data.author,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "filename": filename,
            "ascii": ascii_path  # アスキーアートのパス（含まれていない場合はNone）
        }

        # JSONファイルとしてtweetディレクトリに保存
        json_filename = f"tweet_{tweet_id}.json"
        json_file_path = tweet_dir / json_filename
        
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(tweet_response, f, ensure_ascii=False, indent=2)
        
        response_time = (time.time() - start_time) * 1000
        
        log_request_response(
            request=request,
            response_data=tweet_response,
            status_code=201,
            response_time_ms=response_time,
            request_id=request_id,
            tweet_id=tweet_id,
            filename=filename,
            ascii_path=ascii_path
        )
        
        return tweet_response
        
    except Exception as e:
        error_response_time = (time.time() - start_time) * 1000
        
        log_structured_event(
            "tweet_post_error",
            f"Tweet post failed: {str(e)}",
            level="ERROR",
            request_id=request_id,
            response_time_ms=round(error_response_time, 2),
            error_type=type(e).__name__,
            error_message=str(e),
            status_code=500
        )
        
        raise HTTPException(status_code=500, detail={"error": str(e)}) 
