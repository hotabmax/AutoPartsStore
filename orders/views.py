from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from catalog.models import Product
from .models import Cart, CartItem, Order, OrderItem


def get_or_create_cart(request):
    """Получить или создать корзину для пользователя/сессии"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            session_key=''
        )
    else:
        request.session.modified = True
        # Гарантируем, что сессия сохранена и есть session_key
        if not request.session.session_key:
            request.session.save()
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = get_object_or_404(Cart, id=cart_id, user=None)
        else:
            cart = Cart.objects.create(session_key=request.session.session_key)
            request.session['cart_id'] = cart.id
    return cart


@require_POST
def add_to_cart(request, product_id):
    """Добавить товар в корзину"""
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Валидация количества
    if quantity < 1:
        quantity = 1

    # Проверяем наличие на складе (без учёта корзины — корзина не резервирует)
    if product.stock_quantity < quantity:
        messages.error(
            request,
            f'Доступно только {product.stock_quantity} шт. на складе'
        )
        return redirect('catalog:product_detail', slug=product.slug)

    try:
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, f'{product.name} добавлен в корзину')
    except Exception as e:
        messages.error(request, f'Ошибка при добавлении в корзину: {e}')

    return redirect('orders:cart')


def cart(request):
    """Страница корзины"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'orders/cart.html', context)


@require_POST
def update_cart_item(request, item_id):
    """Обновить количество товара в корзине"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        cart_item.delete()
        messages.success(request, 'Товар удалён из корзины')
    else:
        # Проверяем наличие на складе
        if cart_item.product.stock_quantity < quantity:
            messages.error(
                request,
                f'Доступно только {cart_item.product.stock_quantity} шт. на складе'
            )
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Количество обновлено')

    return redirect('orders:cart')


@require_POST
def remove_from_cart(request, item_id):
    """Удалить товар из корзины"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    messages.success(request, 'Товар удалён из корзины')
    return redirect('orders:cart')


@login_required
def checkout(request):
    """Оформление заказа"""
    # Объединяем сессионную корзину с пользовательской
    session_cart_id = request.session.get('cart_id')
    if session_cart_id:
        session_cart = Cart.objects.filter(id=session_cart_id, user=None).first()
        if session_cart:
            user_cart = Cart.objects.get_or_create(
                user=request.user, session_key=''
            )[0]
            for item in session_cart.items.all():
                cart_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=item.product,
                    defaults={'quantity': item.quantity}
                )
                if not created:
                    cart_item.quantity += item.quantity
                    cart_item.save()
            session_cart.items.all().delete()

    cart, created = Cart.objects.get_or_create(
        user=request.user, session_key=''
    )

    if cart.items.count() == 0:
        messages.error(request, 'Корзина пуста')
        return redirect('catalog:index')

    if request.method == 'POST':
        # Проверяем наличие всех товаров
        for item in cart.items.all():
            if item.product.stock_quantity < item.quantity:
                messages.error(
                    request,
                    f'Недостаточно "{item.product.name}" (нужно: {item.quantity}, доступно: {item.product.stock_quantity})'
                )
                return redirect('orders:cart')

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    phone=request.POST['phone'],
                    email=request.POST['email'],
                    address=request.POST['address'],
                    comment=request.POST.get('comment', ''),
                    total_price=cart.total_price
                )

                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                    # Уменьшаем количество на складе
                    item.product.stock_quantity -= item.quantity
                    item.product.save()

                cart.items.all().delete()

                messages.success(request, 'Заказ успешно оформлен!')
                return redirect('orders:order_success', order_id=order.id)

        except Exception as e:
            messages.error(request, f'Ошибка при оформлении заказа: {e}')

    context = {
        'cart': cart,
    }
    return render(request, 'orders/checkout.html', context)


def order_success(request, order_id):
    """Страница успешного оформления заказа"""
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    return render(request, 'orders/order_success.html', context)


@login_required
def order_history(request):
    """История заказов"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    context = {'orders': orders}
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail(request, order_id):
    """Детали заказа"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user=request.user
    )
    context = {'order': order}
    return render(request, 'orders/order_detail.html', context)


@require_POST
@login_required
def cancel_order(request, order_id):
    """Отмена заказа (удаление)"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        id=order_id,
        user=request.user
    )

    if order.status not in ['new', 'processing']:
        messages.error(request, 'Нельзя отменить заказ в статусе «Отправлен» или «Доставлен»')
        return redirect('orders:order_history')

    # Возвращаем товары на склад
    for item in order.items.all():
        if item.product:
            item.product.stock_quantity += item.quantity
            item.product.save()

    order.delete()
    messages.success(request, f'Заказ #{order_id} отменён')
    return redirect('orders:order_history')
