from fastapi import APIRouter, Request, HTTPException
import json
import time
import uuid
import random
from datetime import datetime
from pathlib import Path
from models.tweet import TweetRequest
from utils.logging import log_structured_event, log_request_response

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
        # 意図的に10000件のダミーデータを生成（パフォーマンス問題）
        dummy_tweets = []
        for i in range(900000):
            dummy_tweets.append({
                "tweet": f"ダミーツイート {i} - " + "🚀" * (i % 10 + 1),
                "like": random.randint(0, 1000),
                "rt": random.randint(0, 500),
                "id": f"dummy_{i}",
                "title": f"ダミータイトル {i}",
                "category": "ダミー",
                "author": f"ダミーユーザー{i % 100}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "filename": f"dummy_{i}.txt"
            })
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
