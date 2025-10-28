# ==============================================================================
# U-AIP Scoping Assistant - Dockerfile
# Multi-stage build for optimized production image with deterministic builds
# ==============================================================================

# ==============================================================================
# Stage 1: Builder - Install dependencies using uv and lockfile
# ==============================================================================
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files (IMPORTANT: uv.lock MUST be copied for deterministic builds)
COPY pyproject.toml uv.lock ./

# Install dependencies using lockfile (deterministic, reproducible builds)
# --frozen ensures exact versions from lockfile, no resolution
RUN uv pip install --system -r pyproject.toml --frozen

# ==============================================================================
# Stage 2: Runtime - Minimal production image
# ==============================================================================
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
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

# Copy Python packages from builder (installed to system Python)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

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
    CMD python -c "import sys; sys.exit(0)"

# Default command (can be overridden)
CMD ["python", "-m", "src.cli.main", "--help"]

# ==============================================================================
# Labels for metadata
# ==============================================================================
LABEL maintainer="U-AIP Team" \
      version="1.0.0-dev" \
      description="Universal AI Project Scoping Assistant - Deterministic builds with uv.lock" \
      org.opencontainers.image.source="https://github.com/yourusername/uaip-scoping-assistant"
