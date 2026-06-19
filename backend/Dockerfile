# ─── Stage: Base Python image ───────────────────────────────────────────────
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Prevents Python from writing .pyc files and buffers stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ─── Install system dependencies ─────────────────────────────────────────────
# Some Python packages (like scikit-learn) may need these at build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ─── Install Python dependencies ─────────────────────────────────────────────
# Copy requirements first so Docker can cache this layer
# (If requirements.txt doesn't change, Docker skips this step on rebuild)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Install gdown to download model from Google Drive ───────────────────────
RUN pip install --no-cache-dir gdown

# ─── Copy application source code ────────────────────────────────────────────
COPY src/ ./src/

# ─── Download the language detection model from Google Drive ─────────────────
# The model is NOT stored in the GitHub repo (it's ~15MB).
# gdown downloads it directly into the image during the build on Render.
# File: language_classification_pipeline.joblib
# Drive ID: 1d1F4mkjGoYHOCOA9cJd2GL7w7BT9Nfg1
RUN mkdir -p /app/models && \
    gdown --id 1d1F4mkjGoYHOCOA9cJd2GL7w7BT9Nfg1 \
          -O /app/models/language_classification_pipeline.joblib

# ─── Set the path to the language model inside the container ─────────────────
# This matches LANG_MODEL_PATH that translator.py reads from the environment
ENV LANG_MODEL_PATH=/app/models/language_classification_pipeline.joblib

# ─── Expose the port FastAPI will run on ─────────────────────────────────────
EXPOSE 8000

# ─── Start the application ───────────────────────────────────────────────────
# We call uvicorn directly (bypassing run.py) to avoid the dev-only reload=True flag
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
