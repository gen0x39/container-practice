from fastapi import FastAPI, Response, Request, HTTPException, File, UploadFile, Form
import json
from fastapi.middleware.cors import CORSMiddleware
import os
import socket
import time
import threading
import glob
from pathlib import Path
import logging
from datetime import datetime
import uuid
from typing import Any, Dict
from pydantic import BaseModel
from PIL import Image
import ascii_magic
import io
import base64
import random
# OpenTelemetry FastAPI Instrumentationの追加
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TweetRequest(BaseModel):
    content: str
    author: str = "ユーザー"
    category: str = "ユーザー投稿"
    ascii_content: str | None = None  # ←アスキーアート本体

# OpenTelemetry用の構造化ログ関数
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

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenTelemetry FastAPI Instrumentationの設定
FastAPIInstrumentor.instrument_app(
    app,
    tracer_provider=None,  # デフォルトのトレーサープロバイダーを使用
    meter_provider=None,   # デフォルトのメータープロバイダーを使用
    excluded_urls=None,    # 除外URLなし
    http_capture_headers_server_request=None,  # リクエストヘッダーキャプチャなし
    http_capture_headers_server_response=None, # レスポンスヘッダーキャプチャなし
    http_capture_headers_sanitize_fields=None, # ヘッダーサニタイズなし
    exclude_spans=None     # スパン除外なし
)

@app.get("/health")
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

@app.get("/")
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

@app.get("/items")
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

@app.get("/ascii-all")
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
                import random
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

        
@app.get("/frontend-info")
def get_frontend_info(request: Request, response: Response):
    """フロントエンドのPod情報を返すエンドポイント"""
    # クライアントのIPアドレスを取得
    client_ip = request.client.host
    
    # 環境判定
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        # Kubernetes環境ではPod名を返す
        pod_name = socket.gethostname()
        pod_ip = socket.gethostbyname(socket.gethostname())
        node_name = os.getenv("NODE_NAME", "unknown")
    else:
        # 開発環境ではMacの情報を返す
        pod_name = socket.getfqdn()
        pod_ip = socket.gethostbyname(socket.gethostname())
        node_name = "localhost"
    
    # レスポンスヘッダーにPod情報を追加
    response.headers["X-Pod-Name"] = pod_name
    response.headers["X-Pod-IP"] = pod_ip
    response.headers["X-Node-Name"] = node_name
    response.headers["X-Client-IP"] = client_ip
    
    return {
        "pod_name": pod_name,
        "pod_ip": pod_ip,
        "node_name": node_name,
        "client_ip": client_ip,
        "environment": env
    }

@app.get("/load-test")
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


@app.get("/tweets")
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
        tweet_dir = Path("tweet")
        if not tweet_dir.exists():
            log_structured_event(
                "tweets_error",
                "Tweet directory not found",
                level="WARNING",
                request_id=request_id,
                error_type="DirectoryNotFound"
            )
            return []
        
        json_files = list(tweet_dir.glob("*.json"))
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
        
        # タイムスタンプでソート（新しい順）
        tweets.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
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


class TweetRequest(BaseModel):
    content: str
    author: str = "ユーザー"
    category: str = "ユーザー投稿"
    ascii_content: str | None = None  # アスキーアートの内容（オプション）

@app.post("/tweet")
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
        has_ascii=tweet_data.ascii_content is not None  # この行も修正
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
        
        if tweet_data.ascii_content:  # この行も修正
            # アスキーアートをファイルに保存
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(tweet_data.ascii_content)  # この行も修正
            ascii_path = f"ascii/{filename}"
            tweet_body = tweet_data.content + "\n" + tweet_data.ascii_content  # この行も修正
            
            log_structured_event(
                "ascii_saved",
                "ASCII art saved to file",
                level="INFO",
                request_id=request_id,
                ascii_path=ascii_path,
                ascii_length=len(tweet_data.ascii_content)  # この行も修正
            )
        
        # レスポンス用のツイートオブジェクトを作成
        tweet_response = {
            "tweet": tweet_body,  # テキスト＋アスキーアート
            "like": random.randint(0, 2000),
            "rt": random.randint(0, 500),
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

@app.post("/upload-image")
async def upload_image_and_convert(
    request: Request,
    file: UploadFile = File(...),
    author: str = Form("ユーザー"),
    category: str = Form("画像変換")
):
    """画像をアップロードしてアスキーアートに変換"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    log_structured_event(
        "image_upload_start",
        "Image upload and conversion started",
        level="INFO",
        request_id=request_id,
        method="POST",
        path="/upload-image",
        filename=file.filename,
        author=author,
        file_size=file.size if file.size else 0
    )
    
    try:
        # ファイル形式チェック
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="画像ファイルのみアップロード可能です")
        
        # ファイルサイズチェック（10MB制限）
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="ファイルサイズは10MB以下にしてください")
        
        # 画像データを読み込み
        image_data = await file.read()
        
        # 一時ファイルとして保存してからascii_magicで処理
        import tempfile
        import os
        
        ascii_content = ""
        temp_file_path = None
        
        try:
            # 一時ファイルに画像を保存
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(image_data)
                temp_file_path = temp_file.name
            
            # ascii_magicでアスキーアート生成（高解像度設定）
            my_art = ascii_magic.from_image(temp_file_path)
            my_output = my_art.to_ascii(
                columns=140,         # 横幅を大幅に増加（より細かい表現）
                monochrome=True,     # 背景色を無効にして純粋なテキストに
                char=None            # デフォルトの文字セットを使用（より豊富な表現）
            )
            ascii_content = str(my_output)
            
            # 標準出力にアスキーアートを出力
            print("=== アップロードされた画像のアスキーアート ===")
            print(ascii_content)
            print("==========================================")
            
            log_structured_event(
                "ascii_conversion_success",
                "ASCII art conversion completed and printed to stdout",
                level="INFO",
                request_id=request_id,
                ascii_length=len(ascii_content),
                columns=200,
                width_ratio=0.5,
                monochrome=True
            )
            
        finally:
            # 一時ファイルを削除
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

        # ツイートIDを生成
        tweet_id = str(uuid.uuid4())
        filename = f"tweet_{tweet_id}.txt"
        
        # asciiディレクトリの作成（存在しない場合）
        ascii_dir = Path("ascii")
        try:
            ascii_dir.mkdir(exist_ok=True, mode=0o755)
        except PermissionError:
            # 権限エラーの場合は/tmpディレクトリを使用
            ascii_dir = Path("/tmp/ascii")
            ascii_dir.mkdir(exist_ok=True, mode=0o755)
        
        # アスキーアートをファイルに保存
        file_path = ascii_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(ascii_content)
        
        # tweetディレクトリにもJSONとして保存
        tweet_dir = Path("tweet")
        try:
            tweet_dir.mkdir(exist_ok=True, mode=0o755)
        except PermissionError:
            # 権限エラーの場合は/tmpディレクトリを使用
            tweet_dir = Path("/tmp/tweet")
            tweet_dir.mkdir(exist_ok=True, mode=0o755)
        
        # レスポンス用のツイートオブジェクトを作成
        tweet_response = {
            "tweet": ascii_content,  # ←ここにアスキーアート本体
            "like": random.randint(0, 2000),
            "rt": random.randint(0, 500),
            "id": tweet_id,
            "title": f"画像変換: {file.filename}",
            "category": category,
            "author": author,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "filename": filename,
            "original_image": file.filename,
            "ascii": f"ascii/{filename}",  # ファイルパス
            "ascii_content": ascii_content # ←アスキーアート本体も返す
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
            original_image=file.filename,
            ascii_length=len(ascii_content),
            ascii_path=f"ascii/{filename}",
            ascii_columns=200,
            width_ratio=0.5,
            monochrome=True
        )
        
        return tweet_response
        
    except HTTPException:
        # HTTPExceptionはそのまま再送出
        raise
    except Exception as e:
        error_response_time = (time.time() - start_time) * 1000
        
        log_structured_event(
            "image_upload_error",
            f"Image upload failed: {str(e)}",
            level="ERROR",
            request_id=request_id,
            response_time_ms=round(error_response_time, 2),
            error_type=type(e).__name__,
            error_message=str(e),
            status_code=500
        )
        
        raise HTTPException(status_code=500, detail={"error": str(e)})
