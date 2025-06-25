# ベースイメージとしてtiangolo/uvicorn-gunicorn-fastapiを使用
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# 作業ディレクトリの設定
WORKDIR /app

# 非rootユーザーの作成
RUN useradd -m -u 1000 appuser

# 必要なディレクトリを作成し、権限を設定
RUN mkdir -p /app/ascii /app/tweet && \
    chown -R appuser:appuser /app

# アプリケーションコードのコピー
COPY --chown=appuser:appuser main.py /app/main.py
COPY --chown=appuser:appuser requirements.txt /app/requirements.txt
COPY --chown=appuser:appuser data.json /app/data.json

# パッケージのインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 環境変数の設定
ENV OTEL_EXPORTER_DATADOG_ENDPOINT=http://datadog-agent:8126
ENV OTEL_SERVICE_NAME=my-fastapi-service
ENV OTEL_TRACES_EXPORTER=datadog
ENV OTEL_METRICS_EXPORTER=none
ENV OTEL_LOGS_EXPORTER=none

# ユーザーの切り替え
USER appuser

# CMDは削除（ベースイメージのデフォルト設定を使用）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
# CMD ["opentelemetry-instrument", "--traces_exporter", "datadog", "--service_name", "my-fastapi-service", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
