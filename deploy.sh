#!/bin/bash
# Production deployment script for Autoshop

set -e

echo "=== Autoshop Production Deployment ==="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your production values!"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Check for security issues
echo "🔍 Checking security settings..."
python manage.py check --deploy

# Create superuser if not exists
echo "👤 Creating superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created')
else:
    print('ℹ️  Superuser already exists')
"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Start the server with:"
echo "  gunicorn autoshop.wsgi --bind 0.0.0.0:8000"
echo ""
echo "Or use the Procfile (Heroku, etc.):"
echo "  gunicorn autoshop.wsgi --bind 0.0.0.0:\$PORT"
