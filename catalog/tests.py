from django.test import TestCase, Client
from django.urls import reverse
from catalog.models import Category, Manufacturer, Product


class CatalogViewsTest(TestCase):
    """Тесты для каталога"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name='Масла',
            slug='oils',
            is_active=True
        )
        self.manufacturer = Manufacturer.objects.create(
            name='Bosch',
            slug='bosch',
            country='Германия'
        )
        self.product = Product.objects.create(
            name='Моторное масло 5W-30',
            slug='motor-oil-5w30',
            article='BOSCH-5W30',
            price=3500.00,
            stock_quantity=10,
            category=self.category,
            manufacturer=self.manufacturer,
            condition='new'
        )

    def test_index_page(self):
        response = self.client.get(reverse('catalog:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'АвтоЗапчасти')
        self.assertTemplateUsed(response, 'catalog/index.html')

    def test_categories_page(self):
        response = self.client.get(reverse('catalog:categories'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Масла')
        self.assertTemplateUsed(response, 'catalog/categories.html')

    def test_category_detail_page(self):
        response = self.client.get(
            reverse('catalog:category_detail', kwargs={'slug': 'oils'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Масла')
        self.assertContains(response, 'Моторное масло 5W-30')

    def test_product_detail_page(self):
        response = self.client.get(
            reverse('catalog:product_detail', kwargs={'slug': 'motor-oil-5w30'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Моторное масло 5W-30')
        self.assertContains(response, '3500')
        self.assertContains(response, 'BOSCH-5W30')

    def test_search_page(self):
        response = self.client.get(
            reverse('catalog:search'),
            {'q': 'масло'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Моторное масло 5W-30')

    def test_search_empty(self):
        response = self.client.get(
            reverse('catalog:search'),
            {'q': 'несуществующийтовар123'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ничего не найдено')


class CartViewsTest(TestCase):
    """Тесты для корзины"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name='Тормоза',
            slug='brakes',
            is_active=True
        )
        self.product = Product.objects.create(
            name='Тормозные колодки',
            slug='brake-pads',
            article='BP-001',
            price=2500.00,
            stock_quantity=5,
            category=self.category,
            condition='new'
        )

    def test_cart_page_empty(self):
        response = self.client.get(reverse('orders:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Корзина')

    def test_add_to_cart(self):
        response = self.client.post(
            reverse('orders:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('orders:cart'))


class AuthViewsTest(TestCase):
    """Тесты для авторизации"""

    def test_register_page(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_login_page(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_register_user(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123',
        })
        self.assertEqual(response.status_code, 302)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_login_user(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username='loginuser',
            password='LoginPass123'
        )
        response = self.client.post(reverse('accounts:login'), {
            'username': 'loginuser',
            'password': 'LoginPass123',
        })
        self.assertEqual(response.status_code, 302)


class ModelsTest(TestCase):
    """Тесты для моделей"""

    def test_category_str(self):
        category = Category.objects.create(
            name='Подвеска',
            slug='suspension'
        )
        self.assertEqual(str(category), 'Подвеска')

    def test_product_str(self):
        category = Category.objects.create(name='Двигатель', slug='engine')
        product = Product.objects.create(
            name='Фильтр масляный',
            slug='oil-filter',
            article='OF-100',
            price=800.00,
            category=category
        )
        self.assertEqual(str(product), 'Фильтр масляный (OF-100)')

    def test_product_slug_auto_generated(self):
        category = Category.objects.create(name='Электрика', slug='electric')
        product = Product.objects.create(
            name='Oil Filter',
            article='OF-100',
            price=800.00,
            category=category
        )
        self.assertTrue(len(product.slug) > 0)
        self.assertEqual(product.slug, 'oil-filter')

    def test_manufacturer_str(self):
        manufacturer = Manufacturer.objects.create(
            name='SKF',
            slug='skf',
            country='Швеция'
        )
        self.assertEqual(str(manufacturer), 'SKF')


class OrderViewsTest(TestCase):
    """Тесты для заказов"""

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            username='orderuser',
            password='OrderPass123'
        )
        self.client = Client()
        self.client.login(username='orderuser', password='OrderPass123')

        self.category = Category.objects.create(
            name='Масла',
            slug='oils',
            is_active=True
        )
        self.product = Product.objects.create(
            name='Моторное масло 5W-30',
            slug='motor-oil-5w30',
            article='BOSCH-5W30',
            price=3500.00,
            stock_quantity=10,
            category=self.category,
            condition='new'
        )

    def test_order_history_page(self):
        from orders.models import Order, OrderItem
        order = Order.objects.create(
            user=self.user,
            first_name='Иван',
            last_name='Петров',
            phone='+79991234567',
            email='test@test.ru',
            address='Москва',
            total_price=3500.00,
            status='new'
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=3500.00
        )
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '#1')

    def test_cancel_order(self):
        from orders.models import Order, OrderItem
        order = Order.objects.create(
            user=self.user,
            first_name='Иван',
            last_name='Петров',
            phone='+79991234567',
            email='test@test.ru',
            address='Москва',
            total_price=3500.00,
            status='new'
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=3500.00
        )
        initial_stock = self.product.stock_quantity
        response = self.client.post(
            reverse('orders:cancel_order', kwargs={'order_id': order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('orders:order_history'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, initial_stock + 2)
        self.assertFalse(Order.objects.filter(id=order.id).exists())

    def test_cancel_order_not_allowed(self):
        from orders.models import Order, OrderItem
        order = Order.objects.create(
            user=self.user,
            first_name='Иван',
            last_name='Петров',
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
