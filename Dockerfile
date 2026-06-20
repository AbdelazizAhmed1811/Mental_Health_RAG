# ─── Stage 1: Build React Frontend ─────────────────────────────────────────────
FROM node:22-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ─── Stage 2: Base Python image ───────────────────────────────────────────────
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Prevents Python from writing .pyc files and buffers stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ─── Install system dependencies ─────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ─── Install Python dependencies ─────────────────────────────────────────────
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir gdown google-auth python-jose[cryptography]

# ─── Copy application source code ────────────────────────────────────────────
COPY backend/ ./backend/

# ─── Copy built frontend from Stage 1 ────────────────────────────────────────
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# ─── Download the language detection model from Google Drive ─────────────────
RUN mkdir -p /app/backend/models && \
    gdown 1d1F4mkjGoYHOCOA9cJd2GL7w7BT9Nfg1 \
          -O /app/backend/models/language_classification_pipeline.joblib

ENV LANG_MODEL_PATH=/app/backend/models/language_classification_pipeline.joblib

EXPOSE 7860

CMD ["uvicorn", "backend.src.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
