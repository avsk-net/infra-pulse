# ── Stage 1: install dependencies ────────────────────────────
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: lean runtime image ──────────────────────────────
FROM python:3.12-slim

# Install ping (needed for check_ping) and curl (for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
      iputils-ping curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy app code
COPY --chown=appuser:appuser app/ ./app/

USER appuser

ARG  APP_VERSION=dev
ENV  APP_VERSION=$APP_VERSION

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

