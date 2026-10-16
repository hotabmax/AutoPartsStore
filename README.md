# АвтоЗапчасти — Интернет-магазин автозапчастей

Django 6.1 — интернет-магазин автозапчастей с каталогом, корзиной, оформлением заказов и системой авторизации.

## 🚀 Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/hotabmax/AutoPartsStore.git
cd AutoPartsStore

# 2. Создать .env
cp .env.example .env

# 3. Запустить через Docker
docker-compose up -d

# 4. Создать суперпользователя
docker-compose exec web python manage.py createsuperuser

# 5. Собрать статику
docker-compose run --rm collectstatic
```

Откройте: http://127.0.0.1:8000/

## 📋 Содержание

- [Возможности](#возможности)
- [Стек технологий](#стек-технологий)
- [Структура проекта](#структура-проекта)
- [Локальный запуск (без Docker)](#локальный-запуск-без-docker)
- [Docker](#docker)
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
| Тестирование | Django Test Framework (44 теста) |
| WSGI | Gunicorn |
| Static files | WhiteNoise |

## Структура проекта

```
Shop/
├── autoshop/           # Конфигурация проекта
│   ├── settings.py     # Настройки (env, middleware, шаблоны)
│   ├── urls.py         # Корневые URL-маршруты
│   └── wsgi.py         # WSGI-конфигурация
├── catalog/            # Приложение каталога
│   ├── models.py       # Category, Manufacturer, Product
│   ├── views.py        # Главная, каталог, поиск, детали
│   ├── admin.py        # Админ-конфигурация
│   └── urls.py         # /categories/, /product/<slug>/, /search/
├── orders/             # Приложение заказов
│   ├── models.py       # Cart, CartItem, Order, OrderItem
│   ├── views.py        # Корзина, checkout, история
│   └── urls.py         # /cart/, /checkout/, /history/
├── accounts/           # Приложение авторизации
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
├── Dockerfile          # Docker-образ приложения
├── docker-compose.yml  # Dev-окружение (Django + PostgreSQL)
├── docker-compose.prod.yml  # Prod-конфигурация
├── .env.example        # Шаблон переменных окружения
├── manage.py           # CLI-утилита Django
└── requirements.txt    # Зависимости
```

## Локальный запуск (без Docker)

### 1. Виртуальное окружение

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
cp .env.example .env
# Отредактировать .env при необходимости
```

### 3. Миграции и суперпользователь

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Запуск

```bash
python manage.py runserver
```

## Docker

### Команды

```bash
# Запустить в фоне
docker-compose up -d

# Остановить
docker-compose down

# Удалить volumes (внимание: данные БД удалятся)
docker-compose down -v

# Логи
docker-compose logs -f web
docker-compose logs -f db

# Выполнить команды
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py shell

# Пересобрать образ
docker-compose build --no-cache
```

### Продакшен

```bash
# Запустить продакшен-конфигурацию
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Собрать и запустить образ
docker build -t autoshop:latest .
docker run -d --name autoshop -p 8000:8000 --env-file .env autoshop:latest
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
