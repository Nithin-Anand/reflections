# syntax=docker/dockerfile:1

# Use UV's official Python image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Set work directory
WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies (without dev dependencies for production)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy project files
COPY journal_project/ ./journal_project/
COPY journal/ ./journal/
COPY tests/ ./tests/
COPY static/ ./static/
COPY manage.py ./
COPY migrate_old_data.py ./
COPY entrypoint.sh ./

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Create directory for SQLite database (will be mounted as volume)
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Default command: run Django development server
# For production, use gunicorn instead
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
