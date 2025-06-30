# Attack.md

## 概要

この文書は、ASCII Twitter Webサービスに対する **O11y（Observability）研修** の一環として、CIA セキュリティ三要素（可用性・完全性・機密性）それぞれを損なう攻撃の可能性を列挙し、想定される挙動・観測ポイント・研修応用のためにまとめたものです。

---

## 1. 可用性 (Availability) を損なう攻撃

| 狙い | 主な手口 | 想定される結果 |
|------|----------|----------------|
| **CPU・メモリ枯渇** | - `/load-test?seconds=…` を並列呼び出し<br>- 巨大画像を変換にかける<br>- `/ascii-all` に大量投稿 | FastAPI プロセスが OOMKill、レスポンス遅延や再起動ループ |
| **ディスク枯渇** | - 最大サイズ画像の大量投稿<br>- 長大 ASCII テキストを連投 | 書き込み不可、ログ出力停止、永続障害化 |
| **FD（ファイルディスクリプタ）枯渇** | - HTTP keep-alive や WebSocket の継続維持 | 接続拒否、サービス劣化 |
| **ランタイム例外** | - malformed画像で Pillow クラッシュ誘発 | サービスクラッシュ、例外未処理で停止 |
| **監視の自己DoS** | - Trace属性数増加 → Collectorメモリ爆発 | 監視不能、トラブル検知不可 |
| **ネットワーク帯域圧迫** | - 非キャッシュAPIを大量並列呼び出し | LBやK8sクラスタの輻輳 |

---

## 2. 完全性 (Integrity) を損なう攻撃

| 狙い | 主な手口 | 想定される結果 |
|------|----------|----------------|
| **ストレージ改ざん** | - パストラバーサルや zip-slip による書換 | 設定/コード書換、永続改竄 |
| **ツイートデータ破壊** | - 構造破壊JSON投稿や特殊文字注入 | 表示崩壊、読み込み不能 |
| **XSS / 不正操作** | - ASCII中に `<script>` を埋め込む | 他人になりすまし投稿 |
| **CSRF風の操作** | - 自動投稿を含むクロスサイトリクエスト | 意図しない状態変更 |
| **ログ偽装・流し** | - 攻撃の直前に大量ログ生成 | 痕跡の隠蔽、分析困難 |
| **依存パッケージ汚染** | - typosquattingライブラリ導入 | 開発段階でバックドア注入 |

---

## 3. 機密性 (Confidentiality) を損なう攻撃

| 狙い | 主な手口 | 想定される結果 |
|------|----------|----------------|
| **内部情報露出** | - `/health`, `/frontend-info` から情報収集 | インフラ構成流出 |
| **CORS & 認証なし** | - クロスサイトJSからAPI呼び出し | ブラウザ経由で情報吸出し |
| **詳細エラー表示** | - 例外発生でstack trace露出 | 内部パス・シークレット流出 |
| **SSRF** | - `169.254.169.254`等への画像取得 | クラウドIAMメタ情報奪取 |
| **ログへの機密入力** | - Authorization等のヘッダを記録させる | ログ経由で資格情報漏洩 |
| **推測しやすいURL** | - ID連番で直接取得など | 非公開情報の閲覧 |
| **TLS無効 or 弱い** | - MITM による通信傍受 | 通信内容の覗き見・改竄 |

---

## 4. 攻撃方針別サマリ

### A. 観測しやすい DoS シナリオ

- `/load-test` により CPU 100% → Pod OOMKill
- 巨大画像でディスク逼迫 → 書き込み不能
- 高カーディナリティな Trace で Collector 死亡

### B. サイレント改ざん

- zip-slip でコード書換 → 攻撃API追加
- 管理者ブラウザへの XSS → セッション情報抜き取り

### C. 情報抜き取り

- 内部ユーザから CORS 経由でデータ exfiltrate
- SSRF でクラウド IAM 資格情報収集

---

## 5. 研修観点の応用

| 観測指標 | 異常検出の例 |
|----------|--------------|
| CPU / メモリ | HPAのスケール動作、再起動回数 |
| ディスク | 書込みエラー、inode 使用率上昇 |
| HTTPエラー | エラー率グラフ、p95レスポンス時間 |
| トレース属性数 | Collectorのメモリ急上昇 |
| アクセスログ | 不審なエンドポイント・多発するPOST |
| ネットワーク | egress監視で内部リソースアクセス検知 |

---

## 注意

本資料は研修・教育目的のものであり、実際に攻撃を行う際は必ず検証環境にて実施し、対象システムの開発者・所有者の許可を得てください。



from fastapi import APIRouter, Request, HTTPException
import json
import time
import uuid
import random
from datetime import datetime
from pathlib import Path
from opentelemetry import trace
from models.tweet import TweetRequest
from utils.logging import log_structured_event, log_request_response

router = APIRouter()
tracer = trace.get_tracer(__name__)

@router.get("/tweets")
async def get_all_tweets(request: Request):
    """tweetディレクトリから全てのツイートを取得"""
    # トレース情報を取得
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x')
    span_id = format(span.get_span_context().span_id, '016x')
    
    print(f"🔍 TRACE DEBUG - TraceId: {trace_id}, SpanId: {span_id}")
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # カスタムスパンを作成
    with tracer.start_as_current_span("get_all_tweets") as span:
        span.set_attribute("request.id", request_id)
        span.set_attribute("endpoint", "/tweets")
        span.set_attribute("method", "GET")
        
        log_structured_event(
            "tweets_request_start",
            "Tweets request started",
            level="INFO",
            request_id=request_id,
            method="GET",
            path="/tweets",
            trace_id=trace_id,
            span_id=span_id
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
            
            # 実際のファイルからツイートを読み込み
            tweet_dir = Path("tweet")
            
            if tweet_dir.exists():
                json_files = list(tweet_dir.glob("*.json"))
                for json_file in json_files:
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            tweet_data = json.load(f)
                            tweets.append(tweet_data)
                    except Exception as e:
                        print(f"Error reading {json_file}: {e}")
            
            # ダミーデータと実際のデータを結合
            all_tweets = dummy_tweets + tweets
            
            # 意図的に10件しか返さない（バグ）
            tweets_to_return = all_tweets[:10]
            
            response_time = (time.time() - start_time) * 1000
            span.set_attribute("response.time_ms", response_time)
            span.set_attribute("tweets.count", len(tweets_to_return))
            span.set_attribute("dummy_tweets.generated", len(dummy_tweets))
            span.set_attribute("actual_tweets.count", len(tweets))
            
            print(f"✅ TRACE DEBUG - Request completed: {response_time}ms")
            print(f"📊 Generated {len(dummy_tweets)} dummy tweets, returned {len(tweets_to_return)}")
            
            return tweets_to_return
            
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            
            print(f"❌ TRACE DEBUG - Error occurred: {str(e)}")
            
            raise HTTPException(status_code=500, detail={"error": str(e)})

# ... existing code ...
