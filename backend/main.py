from fastapi import FastAPI, Response, Request, HTTPException
import json
from fastapi.middleware.cors import CORSMiddleware
import os
import socket
import time
import threading
import glob
from pathlib import Path


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return "Hello World"

@app.get("/items")
async def get_items():
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    with open('data.json', 'r') as f:
        data = json.load(f)
    for item in data:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")

@app.get("/ascii")
async def get_ascii_art_list():
    """ASCIIアートファイルの一覧を取得"""
    ascii_dir = Path("ascii")
    if not ascii_dir.exists():
        return []
    
    # .txtファイルを検索
    txt_files = list(ascii_dir.glob("*.txt"))
    
    ascii_files = []
    for i, file_path in enumerate(txt_files, 1):
        # ファイル名からタイトルを生成
        title = file_path.stem.replace('_', ' ').title()
        
        ascii_files.append({
            "id": i,
            "title": title,
            "filename": file_path.name,
            "category": "アニメ",
            "author": "ASCIIアーティスト"
        })
    
    print(f"ASCIIアートファイル一覧取得: {len(ascii_files)}件")
    return ascii_files

@app.get("/ascii/{filename}")
async def get_ascii_art_content(filename: str):
    """特定のASCIIアートファイルの内容を取得"""
    file_path = Path("ascii") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"ASCIIアートファイル読み込み成功: {filename}, サイズ: {len(content)}文字")
        
        return {
            "filename": filename,
            "content": content,
            "size": len(content)
        }
    except Exception as e:
        print(f"ASCIIアートファイル読み込みエラー: {filename}, エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reading file {filename}")

@app.get("/ascii-all")
async def get_all_ascii_art():
    """すべてのASCIIアートを一度に取得"""
    ascii_dir = Path("ascii")
    if not ascii_dir.exists():
        return []
    
    txt_files = list(ascii_dir.glob("*.txt"))
    ascii_arts = []
    
    for i, file_path in enumerate(txt_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()  # ← ここでファイルの内容を読み込んでいます
            
            title = file_path.stem.replace('_', ' ').title()
            
            ascii_arts.append({
                "id": i,
                "title": title,
                "content": content,  # ← ファイルの内容を返しています
                "category": "アニメ",
                "author": "ASCIIアーティスト",
                "likes": 0
            })
            
            print(f"ASCIIアート読み込み成功: {file_path.name}, サイズ: {len(content)}文字")
            
        except Exception as e:
            print(f"ASCIIアート読み込みエラー: {file_path.name}, エラー: {str(e)}")
    
    return ascii_arts

    
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
