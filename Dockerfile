# =============================================================================
# Vnstock MCP Server — Multi-stage Docker build
# Base:  python:3.10-slim-bullseye (per vnstock deployment guide)
#
# vnstock_data (Bronze+ tier) is installed at runtime via entrypoint.sh
# using the bundled CLI installer + VNSTOCK_API_KEY env var.
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

# Install only base requirements (vnstock, mcp, uvicorn — all public packages)
COPY requirements-base.txt .
RUN pip install --no-cache-dir --prefix=/install \
    --extra-index-url https://vnstocks.com/api/simple \
    -r requirements-base.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.10-slim-bullseye

# Minimal runtime deps + curl for uv installer
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Install uv (needed by vnstock CLI installer for vnstock_data)
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy CLI installer for runtime vnstock_data installation
COPY .build_cli_package/ /app/installer/

# Copy server, installer, and entrypoint
COPY server.py .
COPY install_vnstock_data.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Default env
ENV MCP_TRANSPORT=http \
    MCP_PORT=8000 \
    MCP_HOST=0.0.0.0 \
    LOG_LEVEL=INFO \
    VNSTOCK_API_KEY="" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import socket; s=socket.create_connection(('localhost',8000),timeout=5); s.close()" || exit 1

ENTRYPOINT ["./entrypoint.sh"]
