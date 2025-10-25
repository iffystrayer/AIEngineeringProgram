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
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files and essential source files for build
COPY pyproject.toml ./

# Create virtual environment and install dependencies from pyproject.toml
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip setuptools wheel && \
    /app/.venv/bin/pip install \
        fastapi>=0.104.0 \
        uvicorn>=0.24.0 \
        asyncpg>=0.29.0 \
        psycopg2-binary>=2.9.9 \
        pydantic>=2.5.0 \
        pydantic-settings>=2.1.0 \
        anthropic>=0.18.0 \
        python-jose[cryptography]>=3.3.0 \
        passlib[bcrypt]>=1.7.4 \
        pyyaml>=6.0 \
        python-dotenv>=1.0.0 \
        rich>=13.7.0 \
        click>=8.1.7 \
        httpx>=0.26.0 \
        structlog>=24.1.0 \
        prometheus-client>=0.19.0 \
        markdown-it-py>=3.0.0 \
        weasyprint>=60.2 \
        python-multipart>=0.0.6 \
        alembic>=1.13.0

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
    curl \
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
COPY --chown=uaip:uaip migrations/ /app/migrations/
COPY --chown=uaip:uaip alembic.ini /app/
COPY --chown=uaip:uaip pyproject.toml /app/

# Switch to non-root user
USER uaip

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command (can be overridden)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ==============================================================================
# Labels for metadata
# ==============================================================================
LABEL maintainer="U-AIP Team" \
      version="1.0.0-dev" \
      description="Universal AI Project Scoping Assistant" \
      org.opencontainers.image.source="https://github.com/yourusername/uaip-scoping-assistant"
