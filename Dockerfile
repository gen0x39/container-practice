# ベースイメージとしてtiangolo/uvicorn-gunicorn-fastapiを使用
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# 作業ディレクトリの設定
WORKDIR /app

# 非rootユーザーの作成
RUN useradd -m -u 1000 appuser

# アプリケーションコードのコピー
COPY --chown=appuser:appuser main.py /app/main.py
COPY --chown=appuser:appuser requirements.txt /app/requirements.txt

# パッケージのインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ユーザーの切り替え
USER appuser

# アプリケーションの起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
