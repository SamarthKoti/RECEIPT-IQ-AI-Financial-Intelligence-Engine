FROM node:22-bookworm-slim AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    SERVE_FRONTEND=true COOKIE_SECURE=true STORAGE_DIR=/tmp/receipt-iq-uploads
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ backend/
COPY deploy/ deploy/
COPY --from=frontend /build/dist frontend/dist
RUN useradd --uid 10001 --create-home receipt && chown -R receipt:receipt /app
USER receipt
EXPOSE 10000
CMD ["python", "deploy/start.py"]
