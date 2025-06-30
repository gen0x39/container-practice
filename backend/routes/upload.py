from fastapi import APIRouter, Request, HTTPException, File, UploadFile, Form
import time
import uuid
import random
import tempfile
import os
from datetime import datetime
from pathlib import Path
import ascii_magic
from utils.logging import log_structured_event, log_request_response
import json

router = APIRouter()

@router.post("/upload-image")
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
            "like": random.randint(5000, 100000),
            "rt": random.randint(500, 50000),
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
