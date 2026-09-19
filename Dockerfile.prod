# ============================================
# Stage 1: Build dependencies
# ============================================
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy dependency definition files only (cache layer)
COPY pyproject.toml uv.lock ./

# Install dependencies (no project install yet)
RUN uv sync --frozen --no-install-project --no-dev

# Copy application source code
COPY . .

# Install application project (without dev deps)
RUN uv sync --frozen --no-dev


# ============================================
# Stage 2: Production runtime
# ============================================
FROM python:3.13-slim-bookworm AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# Install runtime system dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Copy built virtualenv and app from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports for FastAPI (8000) and MCP SSE (8001)
EXPOSE 8000 8001

# Health check (flexible: checks FastAPI port 8000 or MCP SSE port 8001)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || curl -s http://localhost:8001/sse > /dev/null || exit 1

# Default command: production uvicorn (no reload, multiple workers)
CMD ["python", "-m", "uvicorn", "app.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--workers", "4", \
    "--proxy-headers", \
    "--forwarded-allow-ips", "*", \
    "--access-log"]
