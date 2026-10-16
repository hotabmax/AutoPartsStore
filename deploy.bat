@echo off
REM Production deployment script for Autoshop (Windows)

echo === Autoshop Production Deployment ===

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found. Copying from .env.example...
    copy .env.example .env
    echo [WARNING] Please edit .env with your production values!
    pause
    exit /b 1
)

REM Install dependencies
echo [1/4] Installing dependencies...
pip install -r requirements.txt

REM Run migrations
echo [2/4] Running migrations...
python manage.py migrate --noinput

REM Collect static files
echo [3/4] Collecting static files...
python manage.py collectstatic --noinput --clear

REM Check for security issues
echo [4/4] Checking security settings...
python manage.py check --deploy

REM Create superuser if not exists
echo Creating superuser...
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

echo.
echo === Deployment complete! ===
echo.
echo Start the server with:
echo   gunicorn autoshop.wsgi --bind 0.0.0.0:8000
echo.
pause
