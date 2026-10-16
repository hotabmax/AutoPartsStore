from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db import models
from .models import Category, Product, Manufacturer
from orders.models import CartItem


def index(request):
    """Главная страница"""
    categories = Category.objects.filter(is_active=True)[:6]
    products = Product.objects.filter(is_active=True)[:8]
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'catalog/index.html', context)


def categories(request):
    """Страница категорий"""
    categories = Category.objects.filter(is_active=True)
    context = {'categories': categories}
    return render(request, 'catalog/categories.html', context)


def category_detail(request, slug):
    """Страница категории"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).order_by('-created_at')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'catalog/category_detail.html', context)


def product_detail(request, slug):
    """Страница товара"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'catalog/product_detail.html', context)


def search(request):
    """Поиск товаров"""
    query = request.GET.get('q', '').strip()
    products = []

    if query:
        products = Product.objects.filter(
            is_active=True
        ).filter(
            models.Q(name__icontains=query) |
            models.Q(article__icontains=query) |
            models.Q(description__icontains=query)
        ).distinct()

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'page_obj': page_obj,
    }
    return render(request, 'catalog/search.html', context)
