# ==============================================================================
# U-AIP Scoping Assistant - Dockerfile
# Multi-stage build for optimized production image
# ==============================================================================

# ==============================================================================
# Stage 1: Builder - Install dependencies
# ==============================================================================
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip setuptools wheel && \
    /app/.venv/bin/pip install \
        anthropic \
        asyncpg \
        rich \
        click \
        python-dotenv \
        structlog

# ==============================================================================
# Stage 2: Runtime - Minimal production image
# ==============================================================================
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash uaip && \
    mkdir -p /app /app/data /app/logs /app/charters && \
    chown -R uaip:uaip /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=uaip:uaip /app/.venv /app/.venv

# Copy application code
COPY --chown=uaip:uaip src/ /app/src/
COPY --chown=uaip:uaip database/ /app/database/
COPY --chown=uaip:uaip pyproject.toml /app/

# Switch to non-root user
USER uaip

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (can be overridden)
CMD ["python", "-m", "src.cli.main", "--help"]

# ==============================================================================
# Labels for metadata
# ==============================================================================
LABEL maintainer="U-AIP Team" \
      version="1.0.0-dev" \
      description="Universal AI Project Scoping Assistant" \
      org.opencontainers.image.source="https://github.com/yourusername/uaip-scoping-assistant"
