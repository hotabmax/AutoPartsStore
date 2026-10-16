# syntax=docker/dockerfile:1

# ===== Базовый образ =====
FROM python:3.12-slim

# ===== Переменные окружения =====
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ===== Системные зависимости =====
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ===== Рабочая директория =====
WORKDIR /app

# ===== Копирование зависимостей =====
COPY requirements.txt .

# ===== Установка Python-зависимостей =====
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ===== Копирование проекта =====
COPY . .

# ===== Создание пользователя =====
RUN groupadd -r django && useradd -r -g django django && \
    chown -R django:django /app

# ===== Переключение на пользователя =====
USER django

# ===== Порт =====
EXPOSE 8000

# ===== Health check =====
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python manage.py check --deploy || exit 1

# ===== Запуск =====
CMD ["gunicorn", "autoshop.wsgi", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
