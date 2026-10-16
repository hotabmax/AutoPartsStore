"""Тестирование всех форм проекта"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Category, Product
from orders.models import Cart, CartItem, Order, OrderItem

User = get_user_model()


class FormIntegrationTest(TestCase):
    """Интеграционные тесты для всех форм"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name='Масла', slug='oils', is_active=True
        )
        self.product = Product.objects.create(
            name='Моторное масло 5W-30',
            slug='motor-oil-5w30',
            article='OIL-001',
            price=3500.00,
            stock_quantity=10,
            category=self.category,
            condition='new'
        )

    # ===== ФОРМА РЕГИСТРАЦИИ =====
    def test_register_form_valid(self):
        """Валидная регистрация"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'new@test.ru',
            'password1': 'SecurePass123',
            'password2': 'SecurePass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_form_passwords_mismatch(self):
        """Пароли не совпадают"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'baduser',
            'email': 'bad@test.ru',
            'password1': 'Pass12345',
            'password2': 'Different1',
        })
        self.assertEqual(response.status_code, 200)  # Ошибка валидации
        self.assertFalse(User.objects.filter(username='baduser').exists())

    def test_register_form_weak_password(self):
        """Слабый пароль отклоняется"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'weakuser',
            'email': 'weak@test.ru',
            'password1': 'password',
            'password2': 'password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='weakuser').exists())

    def test_register_form_duplicate_username(self):
        """Дубликат имени пользователя"""
        User.objects.create_user('existing', 'ex@test.ru', 'Existing123')
        response = self.client.post(reverse('accounts:register'), {
            'username': 'existing',
            'email': 'other@test.ru',
            'password1': 'SecurePass123',
            'password2': 'SecurePass123',
        })
        self.assertEqual(response.status_code, 200)  # Ошибка валидации

    def test_register_form_redirects_authenticated(self):
        """Авторизованный пользователь перенаправляется"""
        User.objects.create_user('logged', 'logged@test.ru', 'Logged123')
        self.client.login(username='logged', password='Logged123')
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 302)

    # ===== ФОРМА ВХОДА =====
    def test_login_form_valid(self):
        """Валидный вход"""
        User.objects.create_user('loginuser', 'login@test.ru', 'LoginPass123')
        response = self.client.post(reverse('accounts:login'), {
            'username': 'loginuser',
            'password': 'LoginPass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_form_wrong_password(self):
        """Неверный пароль"""
        User.objects.create_user('wrongpass', 'wp@test.ru', 'Correct123')
        response = self.client.post(reverse('accounts:login'), {
            'username': 'wrongpass',
            'password': 'WrongPassword1',
        })
        self.assertEqual(response.status_code, 200)  # Ошибка валидации

    def test_login_form_redirects_authenticated(self):
        """Авторизованный пользователь перенаправляется"""
        User.objects.create_user('already', 'al@test.ru', 'Already123')
        self.client.login(username='already', password='Already123')
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 302)

    # ===== ФОРМА ПОИСКА =====
    def test_search_form_valid(self):
        """Поиск по существующему товару"""
        response = self.client.get(reverse('catalog:search'), {'q': 'масло'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Моторное масло')

    def test_search_form_empty(self):
        """Пустой поиск"""
        response = self.client.get(reverse('catalog:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_form_no_results(self):
        """Поиск без результатов"""
        response = self.client.get(reverse('catalog:search'), {'q': 'xyz123abc'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ничего не найдено')

    # ===== ФОРМА ДОБАВЛЕНИЯ В КОРЗИНУ =====
    def test_add_to_cart_form_valid(self):
        """Добавление в корзину — валидно"""
        response = self.client.post(
            reverse('orders:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('orders:cart'))
        cart = Cart.objects.get(session_key=self.client.session.session_key)
        self.assertEqual(cart.items.first().quantity, 2)

    def test_add_to_cart_quantity_zero(self):
        """Добавление 0 штук — минимальное 1"""
        response = self.client.post(
            reverse('orders:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 0}
        )
        self.assertEqual(response.status_code, 302)
        cart = Cart.objects.get(session_key=self.client.session.session_key)
        self.assertEqual(cart.items.first().quantity, 1)  # Минимум 1

    def test_add_to_cart_exceeds_stock(self):
        """Превышение количества на складе"""
        response = self.client.post(
            reverse('orders:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 100}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/product/motor-oil-5w30/')

    def test_add_to_cart_negative(self):
        """Отрицательное количество"""
        response = self.client.post(
            reverse('orders:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': -5}
        )
        self.assertEqual(response.status_code, 302)

    # ===== ФОРМА ОБНОВЛЕНИЯ КОРЗИНЫ =====
    def test_update_cart_form_valid(self):
        """Обновление количества в корзине"""
        # Сначала добавим товар
        self.client.post(
            reverse('orders:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )
        cart = Cart.objects.get(session_key=self.client.session.session_key)
        item = cart.items.first()

        # Обновим количество
        response = self.client.post(
            reverse('orders:update_cart_item', kwargs={'item_id': item.id}),
            {'quantity': 5}
        )
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_update_cart_exceeds_stock(self):
        """Превышение лимита при обновлении"""
        self.client.post(
            reverse('orders:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )
        cart = Cart.objects.get(session_key=self.client.session.session_key)
        item = cart.items.first()

        # Пытаемся установить больше чем на складе
        response = self.client.post(
            reverse('orders:update_cart_item', kwargs={'item_id': item.id}),
            {'quantity': 999}
        )
        self.assertEqual(response.status_code, 302)

    def test_update_cart_delete(self):
        """Удаление товара из корзины (quantity=0)"""
        self.client.post(
            reverse('orders:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 3}
        )
        cart = Cart.objects.get(session_key=self.client.session.session_key)
        item = cart.items.first()

        response = self.client.post(
            reverse('orders:update_cart_item', kwargs={'item_id': item.id}),
            {'quantity': 0}
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    # ===== ФОРМА УДАЛЕНИЯ ИЗ КОРЗИНЫ =====
    def test_remove_from_cart(self):
        """Удаление товара из корзины"""
        initial_stock = self.product.stock_quantity
        self.client.post(
            reverse('orders:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 1}
        )
        cart = Cart.objects.get(session_key=self.client.session.session_key)
        item = cart.items.first()

        response = self.client.post(
            reverse('orders:remove_from_cart', kwargs={'item_id': item.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())
        # Склад не меняется при удалении из корзины
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, initial_stock)

    # ===== ФОРМА ОФОРМЛЕНИЯ ЗАКАЗА =====
    def test_checkout_form_valid(self):
        """Валидное оформление заказа"""
        user = User.objects.create_user('checkoutuser', 'checkout@test.ru', 'Checkout123')
        self.client.login(username='checkoutuser', password='Checkout123')

        # Добавляем товар
        self.client.post(
            reverse('orders:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )

        response = self.client.post(reverse('orders:checkout'), {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'phone': '+79991234567',
            'email': 'ivan@test.ru',
            'address': 'Москва, ул. Тестовая, 1',
            'comment': 'Быстрая доставка',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Order.objects.filter(user=user).exists())

    def test_checkout_form_empty_cart(self):
        """Пустая корзина при оформлении"""
        user = User.objects.create_user('emptycart', 'empty@test.ru', 'Empty123')
        self.client.login(username='emptycart', password='Empty123')

        response = self.client.post(reverse('orders:checkout'), {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'phone': '+79991234567',
            'email': 'ivan@test.ru',
            'address': 'Москва, ул. Тестовая, 1',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('catalog:index'))

    def test_checkout_form_missing_fields(self):
        """Не заполнены обязательные поля"""
        user = User.objects.create_user('missing', 'miss@test.ru', 'Miss123')
        self.client.login(username='missing', password='Miss123')

        # Добавляем товар
        self.client.post(
            reverse('orders:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 1}
        )

        response = self.client.post(reverse('orders:checkout'), {
            'first_name': '',
            'last_name': '',
            'phone': '',
            'email': '',
            'address': '',
        })
        # Форма не имеет валидации на уровне views, данные сохраняются
        self.assertEqual(response.status_code, 302)

    # ===== ФОРМА ОТМЕНЫ ЗАКАЗА =====
    def test_cancel_order_form(self):
        """Отмена заказа"""
        user = User.objects.create_user('canceluser', 'cancel@test.ru', 'Cancel123')
        self.client.login(username='canceluser', password='Cancel123')

        order = Order.objects.create(
            user=user,
            first_name='Иван',
            last_name='Иванов',
            phone='+79991234567',
            email='test@test.ru',
            address='Москва',
            total_price=7000.00,
            status='new'
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=3500.00
        )

        response = self.client.post(
            reverse('orders:cancel_order', kwargs={'order_id': order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('orders:order_history'))

    def test_cancel_order_not_allowed(self):
        """Нельзя отменить доставленный заказ"""
        user = User.objects.create_user('deluser', 'del@test.ru', 'Del123')
        self.client.login(username='deluser', password='Del123')

        order = Order.objects.create(
            user=user,
            first_name='Иван',
            last_name='Иванов',
            phone='+79991234567',
            email='test@test.ru',
            address='Москва',
            total_price=3500.00,
            status='delivered'
        )

        response = self.client.post(
            reverse('orders:cancel_order', kwargs={'order_id': order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Order.objects.filter(id=order.id).exists())

    # ===== ФОРМА ВЫХОДА =====
    def test_logout_form(self):
        """Выход из системы"""
        User.objects.create_user('logoutuser', 'logout@test.ru', 'Logout123')
        self.client.login(username='logoutuser', password='Logout123')

        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
