# ============================================================================
# Stage 1: Build Frontend Assets
# ============================================================================
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

# Copy package files and install dependencies
# NOTE: We need devDependencies for build (Vite, TypeScript, etc.)
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# ============================================================================
# Stage 2: Build Python Dependencies
# ============================================================================
FROM python:3.14-slim AS python-builder

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements/base.txt requirements/production.txt requirements/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/production.txt

# ============================================================================
# Stage 3: Final Production Image
# ============================================================================
FROM python:3.14-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 django && \
    mkdir -p /app/logs /app/staticfiles /app/media && \
    chown -R django:django /app

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=python-builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=python-builder /usr/local/bin /usr/local/bin

# Copy frontend build artifacts
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

# Copy application code
COPY --chown=django:django . .

# Copy and set up entrypoint script
COPY --chown=django:django docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Switch to non-root user
USER django

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Expose port
EXPOSE 8000

# Note: Health checks are defined in docker-compose.yml per-service
# Web service checks /api/health/, celery services check broker connectivity

# Set entrypoint and default command
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-4} --timeout 30 --access-logfile - --error-logfile -"]
