# ベースイメージとしてtiangolo/uvicorn-gunicorn-fastapiを使用
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# 作業ディレクトリの設定
WORKDIR /app

# 非rootユーザーの作成
RUN useradd -m -u 1000 appuser

# 必要なディレクトリを作成し、権限を設定
RUN mkdir -p /app/ascii /app/tweet && \
    chown -R appuser:appuser /app

COPY --chown=appuser:appuser main.py /app/main.py
COPY --chown=appuser:appuser data.json /app/data.json
COPY --chown=appuser:appuser models /app/models
COPY --chown=appuser:appuser routes /app/routes
COPY --chown=appuser:appuser utils /app/utils
COPY --chown=appuser:appuser requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV OTEL_SERVICE_NAME=backend-service
ENV OTEL_TRACES_EXPORTER=datadog
ENV OTEL_EXPORTER_DATADOG_ENDPOINT=http://datadog-agent.monitoring.svc.cluster.local:8126
ENV OTEL_RESOURCE_ATTRIBUTES=service.name=backend-service,service.version=1.0.0,deployment.environment=production

# ユーザーの切り替え
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
