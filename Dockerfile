# =============================================================================
# Vnstock MCP Server — Multi-stage Docker build
# Base:  python:3.10-slim-bullseye (per vnstock deployment guide)
# =============================================================================

# ---------- Stage 1: Builder ----------
FROM python:3.10-slim-bullseye AS builder

# Build deps required by vnstock C++ extensions (vnstock_ta, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.10-slim-bullseye

# Minimal runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

WORKDIR /app
COPY server.py .

# Default env
ENV MCP_TRANSPORT=http \
    MCP_PORT=8000 \
    MCP_HOST=0.0.0.0 \
    LOG_LEVEL=INFO \
    VNSTOCK_API_KEY="" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

ENTRYPOINT ["python", "server.py"]
