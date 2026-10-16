# АвтоЗапчасти — Интернет-магазин автозапчастей

Django 6.1 — интернет-магазин автозапчастей с каталогом, корзиной, оформлением заказов и системой авторизации.

## 📋 Содержание

- [Возможности](#возможности)
- [Стек технологий](#стек-технологий)
- [Структура проекта](#структура-проекта)
- [Установка и запуск](#установка-и-запуск)
- [Производственный деплой](#производственный-деплой)
- [Админ-панель](#админ-панель)
- [Модели данных](#модели-данных)
- [API endpoints](#api-endpoints)
- [Тестирование](#тестирование)
- [Разработка](#разработка)

## Возможности

- Каталог товаров с категориями и производителями
- Поиск по названию, артикулу и описанию
- Корзина (для авторизованных и анонимных пользователей)
- Оформление заказа с проверкой наличия
- История заказов и детальный просмотр
- Отмена заказа (возврат на склад)
- Регистрация и авторизация пользователей
- Админ-панель для управления товарами и заказами
- Адаптивный дизайн на Bootstrap 5

## Стек технологий

| Компонент | Технология |
|-----------|-----------|
| Язык | Python 3.12 |
| Фреймворк | Django 6.1 |
| База данных | SQLite (dev) / PostgreSQL (prod) |
| Фронтенд | Bootstrap 5.3, Font Awesome 6 |
| Изображения | Pillow 10+ |
| Тестирование | Django Test Framework |
| WSGI | Gunicorn |
| Static files | WhiteNoise |

## Структура проекта

```
Shop/
├── autoshop/           # Конфигурация проекта
│   ├── settings.py     # Настройки (приложения, middleware, шаблоны)
│   ├── urls.py         # Корневые URL-маршруты
│   ├── wsgi.py         # WSGI-конфигурация
│   └── asgi.py         # ASGI-конфигурация
├── catalog/            # Приложение каталога
│   ├── models.py       # Category, Manufacturer, Product
│   ├── views.py        # Главная, каталог, поиск, детали
│   ├── admin.py        # Админ-конфигурация
│   ├── urls.py         # /categories/, /product/<slug>/, /search/
│   └── tests.py        # Unit-тесты
├── orders/             # Приложение заказов
│   ├── models.py       # Cart, CartItem, Order, OrderItem
│   ├── views.py        # Корзина, checkout, история
│   ├── admin.py        # Админ-конфигурация
│   └── urls.py         # /cart/, /checkout/, /history/
├── accounts/           # Приложение авторизации
│   ├── models.py       # UserProfile
│   ├── views.py        # register, login, logout
│   ├── forms.py        # UserRegisterForm, UserLoginForm
│   └── urls.py         # /accounts/register/, /login/, /logout/
├── templates/          # HTML-шаблоны
│   ├── base.html       # Базовый шаблон с навигацией
│   ├── catalog/        # Шаблоны каталога
│   ├── orders/         # Шаблоны заказов
│   └── accounts/       # Шаблоны авторизации
├── static/             # Статические файлы
│   └── css/style.css   # Кастомные стили
├── media/              # Загруженные файлы (изображения)
├── manage.py           # CLI-утилита Django
└── requirements.txt    # Зависимости
```

## Установка и запуск

### 1. Клонирование

```bash
git clone https://github.com/hotabmax/Shop.git
cd Shop
```

### 2. Виртуальное окружение

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Миграции

```bash
python manage.py migrate
```

### 4. Суперпользователь

```bash
python manage.py createsuperuser
# Логин: admin, Пароль: admin123 (или свой)
```

### 5. Запуск сервера

```bash
python manage.py runserver
```

Откройте: http://127.0.0.1:8000/

## Производственный деплой

### 1. Настройка окружения

```bash
# Скопировать пример окружения
cp .env.example .env

# Или создать вручную
echo "DJANGO_SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" > .env
echo "DJANGO_DEBUG=False" >> .env
echo "DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com" >> .env
```

### 2. База данных

**PostgreSQL (рекомендуется):**
```bash
# Установить драйвер
pip install psycopg2-binary

# Настроить в .env
DB_NAME=autoshop
DB_USER=autoshop
DB_PASSWORD=your-strong-password
DB_HOST=localhost
DB_PORT=5432
```

**SQLite (для тестирования):**
```bash
# Работает по умолчанию при DEBUG=True
```

### 3. Сбор статических файлов

```bash
python manage.py collectstatic --noinput --clear
```

### 4. Запуск в продакшене

**Gunicorn (WSGI сервер):**
```bash
pip install gunicorn
gunicorn autoshop.wsgi --bind 0.0.0.0:8000 --workers 3 --timeout 120
```

**С Procfile (Heroku, Railway, etc.):**
```bash
gunicorn autoshop.wsgi --bind 0.0.0.0:$PORT
```

### 5. Nginx (опционально)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/project/staticfiles/;
    }

    location /media/ {
        alias /path/to/project/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 7. systemd (автостарт)

```ini
# /etc/systemd/system/autoshop.service
[Unit]
Description=Autoshop Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/project/venv/bin/gunicorn autoshop.wsgi --bind 127.0.0.1:8000
EnvironmentFile=/path/to/project/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable autoshop
sudo systemctl start autoshop
```

## Админ-панель

URL: http://127.0.0.1:8000/admin/

| Модель | Поля |
|--------|------|
| **Category** | name, slug, description, image, is_active |
| **Manufacturer** | name, slug, country, description, is_active |
| **Product** | name, slug, article, category, manufacturer, price, stock_quantity, condition, image, is_active |
| **Order** | user, first/last_name, phone, email, address, status, total_price |

## Модели данных

### Catalog

```
Category ──< Product
Manufacturer ──< Product
```

### Orders

```
User ──< Cart ──< CartItem ──> Product
User ──< Order ──< OrderItem ──> Product
```

### Accounts

```
User ──1:1─> UserProfile
```

## API endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | Главная страница |
| GET | `/categories/` | Список категорий |
| GET | `/categories/<slug>/` | Товары категории |
| GET | `/product/<slug>/` | Детали товара |
| GET | `/search/?q=` | Поиск товаров |
| POST | `/orders/cart/add/<id>/` | Добавить в корзину |
| GET | `/orders/cart/` | Страница корзины |
| POST | `/orders/cart/update/<id>/` | Обновить количество |
| POST | `/orders/cart/remove/<id>/` | Удалить из корзины |
| GET | `/orders/checkout/` | Оформление заказа |
| POST | `/orders/checkout/` | Отправка заказа |
| GET | `/orders/order/success/<id>/` | Подтверждение заказа |
| GET | `/orders/history/` | История заказов |
| GET | `/orders/history/<id>/` | Детали заказа |
| POST | `/orders/cancel/<id>/` | Отмена заказа |
| GET/POST | `/accounts/register/` | Регистрация |
| GET/POST | `/accounts/login/` | Вход |
| GET | `/accounts/logout/` | Выход |

## Тестирование

```bash
# Все тесты
python manage.py test

# С подробным выводом
python manage.py test -v 2

# Конкретный модуль
python manage.py test catalog.tests
python manage.py test catalog.tests_forms
```

**44 теста** покрывают:
- Модели (Category, Manufacturer, Product, Order)
- Views каталога (index, categories, detail, search)
- Views корзины (add, empty)
- Авторизация (register, login, logout)
- Заказы (history, cancel)
- Интеграционные тесты форм (25 тестов)

## Разработка

### Добавление нового товара

1. Войти в админ-панель
2. Создать Category (если нет)
3. Создать Manufacturer (если нет)
4. Создать Product с артикулом, ценой и остатком

### Добавление нового приложения

```bash
python manage.py startapp myapp
# 1. Добавить в INSTALLED_APPS
# 2. Создать urls.py и views.py
# 3. Подключить в autoshop/urls.py
```

### Смена базы данных

В `settings.py` заменить `DATABASES` на PostgreSQL/MySQL.
