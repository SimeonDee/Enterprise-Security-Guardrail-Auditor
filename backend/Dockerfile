# ---------- build stage ----------
FROM python:3.11-slim AS builder

WORKDIR /build

COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install . \
    && pip install --no-cache-dir --prefix=/install uvicorn[standard]

# ---------- runtime stage ----------
FROM python:3.11-slim

# Security: run as non-root
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Create data directory for SQLite persistence and set ownership
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
