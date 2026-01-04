#!/bin/bash
set -e

# Wait for database to be ready (if using external DB in future)
# For SQLite, this is not needed but good for future PostgreSQL migration

# Run database migrations
echo "Running database migrations..."
uv run python manage.py migrate --noinput

# Collect static files (for production)
echo "Collecting static files..."
uv run python manage.py collectstatic --noinput --clear || true

# Create superuser if it doesn't exist (optional, for initial setup)
# Uncomment and set environment variables if needed
# echo "Creating superuser..."
# uv run python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

echo "Starting application..."
exec "$@"
