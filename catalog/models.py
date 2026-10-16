from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Категории товаров"""
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='categories/', blank=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    """Производители запчастей"""
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    country = models.CharField('Страна', max_length=100, blank=True)
    description = models.TextField('Описание', blank=True)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товары (запчасти)"""
    condition = models.CharField(
        'Состояние',
        max_length=20,
        choices=[('new', 'Новая'), ('used', 'Б/У')],
        default='new'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Производитель'
    )
    name = models.CharField('Название', max_length=300)
    slug = models.SlugField('URL', max_length=300, unique=True)
    description = models.TextField('Описание', blank=True)
    article = models.CharField('Артикул', max_length=100, unique=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField('Количество на складе', default=0)
    image = models.ImageField('Изображение', upload_to='products/', blank=True)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.article})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
