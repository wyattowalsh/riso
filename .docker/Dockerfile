# syntax=docker/dockerfile:1.11

# =============================================================================
# Multi-stage Production Dockerfile for Riso-generated projects
# =============================================================================
# Supports: Python 3.11+, Node.js 20+, Rust 1.80+
# Security: Non-root users, health checks, minimal attack surface
# Performance: Multi-stage builds, layer caching, BuildKit optimizations
#
# Build stages:
# - builder-python: Python dependency installation with uv
# - builder-node: Node.js dependency installation with pnpm
# - builder-rust: Rust compilation with cargo
# - runtime-python: Minimal Python runtime
# - runtime-node: Minimal Node.js runtime
# - runtime-rust: Minimal Rust runtime
#
# Usage:
#   docker build -t changelog-python:latest .
#   docker build --target runtime-python -t changelog-python-api:latest .
#
# PRODUCTION NOTE: Pin base images with SHA256 digests for reproducibility:
#   python:3.12-slim-bookworm@sha256:abc123...
#   node:20-alpine@sha256:def456...
# Find digests: docker pull <image> && docker inspect <image> | grep -A1 RepoDigests

# =============================================================================
# Python Builder Stage
# =============================================================================
FROM python:3.12-slim-bookworm AS builder-python

# Metadata labels (OCI annotations)
LABEL org.opencontainers.image.title="Changelog Python"
LABEL org.opencontainers.image.description="Changelog Python - Python services"
LABEL org.opencontainers.image.vendor="Riso Template"
LABEL org.opencontainers.image.source="https://github.com/changelog-python"

# Install system dependencies needed for compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast, reproducible dependency management
RUN pip install --no-cache-dir uv==0.5.15

WORKDIR /build

# Copy dependency manifests first for optimal layer caching
COPY pyproject.toml uv.lock ./
COPY README.md ./

# Install dependencies with uv (production only, frozen lockfile)
# BuildKit cache mount accelerates repeated builds
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY src/ ./src/
COPY tests/ ./tests/

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen --no-dev

# =============================================================================
# Python Runtime Stage
# =============================================================================
FROM python:3.12-slim-bookworm AS runtime-python

# Metadata labels
LABEL org.opencontainers.image.title="Changelog Python - Python Runtime"
LABEL org.opencontainers.image.description="Production runtime for Changelog Python Python services"

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user with explicit UID/GID (security best practice)
# UID 1000 is standard for Kubernetes and cloud platforms
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy virtual environment and source from builder
COPY --from=builder-python --chown=1000:1000 /build/.venv /app/.venv
COPY --from=builder-python --chown=1000:1000 /build/src /app/src
COPY --from=builder-python --chown=1000:1000 /build/tests /app/tests

# Environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1

# Switch to non-root user
USER 1000:1000
# Expose FastAPI port
EXPOSE 8000

# Health check for container orchestration
# Checks /health endpoint with retries and backoff
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Default command: Run FastAPI with uvicorn
CMD ["python", "-m", "uvicorn", "changelog_python.api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "info"]
