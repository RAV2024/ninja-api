from django.test import TestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
import json
from .models import *

class CategoryApiTests(TestCase):
    fixtures = ['data.json']

    def test_get_categories_valid(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)

    def test_get_categories_invalid_endpoint(self):
        response = self.client.get("/api/category/")
        self.assertEqual(response.status_code, 404)

    def test_create_category_valid(self):
        payload = {
            'title': 'Смартфоны',
            'slug': 'smartphones'
        }
        response = self.client.post('/api/categories/', content_type='application/json', data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Смартфоны')

    def test_create_category_invalid_data(self):
        payload = {'slug': 'no-title'}
        response = self.client.post('/api/categories/', content_type='application/json', data=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_category_broken_schema(self):
        response = self.client.post('/api/categories/', content_type='text/plain', data='random text')
        self.assertEqual(response.status_code, 400)

    def test_get_category_valid(self):
        response = self.client.get('/api/categories/televizory')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['slug'], 'televizory')

    def test_get_category_invalid_slug(self):
        response = self.client.get('/api/categories/notfound')
        self.assertEqual(response.status_code, 404)

    def test_get_category_broken_slug_type(self):
        response = self.client.get('/api/categories/123!@#')
        self.assertIn(response.status_code, [404, 422])

    def test_delete_category_valid(self):
        response = self.client.delete('/api/categories/televizory')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True})

    def test_delete_category_invalid_slug(self):
        response = self.client.delete('/api/categories/no-such-slug')
        self.assertEqual(response.status_code, 404)

    def test_get_products_in_category_valid(self):
        response = self.client.get('/api/categories/televizory/products')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_get_products_in_category_invalid_slug(self):
        response = self.client.get('/api/categories/nonexistent/products')
        self.assertEqual(response.status_code, 404)


class ProductApiTests(TestCase):
    fixtures = ['data.json']

    def test_list_products_valid(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_list_products_invalid_filter(self):
        response = self.client.get("/api/products/?min_price=invalid")
        self.assertEqual(response.status_code, 422)

    def test_list_products_broken_structure(self):
        # эмулируем ошибку парсера запроса с невалидной строкой
        response = self.client.get("/api/products/?min_price=")
        self.assertEqual(response.status_code, 422)

    def test_create_product_valid(self):
        payload = {
            "title": "LG OLED",
            "category": "televizory",
            "description": "Новый OLED телевизор",
            "price": 70000
        }
        response = self.client.post(
            "/api/products/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['title'], "LG OLED")

    def test_create_product_invalid_category(self):
        payload = {
            "title": "LG OLED",
            "category": "no-category",
            "description": "Новый OLED телевизор",
            "price": 70000
        }
        response = self.client.post(
            "/api/products/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "Категория не найдена"})

    def test_create_product_broken(self):
        payload = {
            "title": "LG OLED",
            "description": "Описание",
            "price": 70000
        }
        response = self.client.post(
            "/api/products/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_get_product_valid(self):
        response = self.client.get("/api/products/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], "Samsung QLED")

    def test_get_product_invalid(self):
        response = self.client.get("/api/products/999")
        self.assertEqual(response.status_code, 404)

    def test_get_product_broken(self):
        response = self.client.get("/api/products/abc")
        self.assertEqual(response.status_code, 422)

    def test_update_product_valid(self):
        payload = {
            "title": "Обновленный Samsung",
            "category": "televizory",
            "description": "Обновленное описание",
            "price": 60000
        }
        response = self.client.patch(
            "/api/products/1",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], "Обновленный Samsung")

    def test_update_product_invalid_category(self):
        payload = {
            "title": "Обновленный Samsung",
            "category": "wrong-category",
            "description": "Обновленное описание",
            "price": 60000
        }
        response = self.client.patch(
            "/api/products/1",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_update_product_broken_schema(self):
        # Ошибка в структуре - неверный тип price
        payload = {
            "title": "Samsung",
            "category": "televizory",
            "description": "Описание",
            "price": "cheap"
        }
        response = self.client.patch(
            "/api/products/1",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 422)

    def test_delete_product_valid(self):
        response = self.client.delete("/api/products/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})

    def test_delete_product_invalid(self):
        response = self.client.delete("/api/products/999")
        self.assertEqual(response.status_code, 404)

    def test_delete_product_broken(self):
        response = self.client.delete("/api/products/abc")
        self.assertEqual(response.status_code, 422)


class AuthTestCase(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            username='admin',
            password='admin',
            first_name='Test',
            last_name='User',
            email='admin@test.com'
        )

    def test_login_success(self):
        payload = {
            "username": "admin",
            "password": "admin"
        }
        response = self.client.post(
            "/api/auth/login",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("token", response_data)
        token = Token.objects.get(user=self.test_user)
        self.assertEqual(response_data["token"], token.key)

    def test_login_failure(self):
        payload = {
            "username": "admin",
            "password": "wrongpassword"
        }
        response = self.client.post(
            "/api/auth/login",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Неверные учетные данные"})

    def test_register_success(self):
        payload = {
            "username": "newuser",
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@test.com",
            "is_manager": False
        }
        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("token", response_data)
        user = User.objects.get(username="newuser")
        self.assertTrue(user.check_password("newpassword"))

    def test_register_existing_user(self):
        payload = {
            "username": "admin",
            "password": "admin",
            "first_name": "Existed",
            "last_name": "User",
            "email": "admin@test.com",
            "is_manager": False
        }
        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Пользователь с таким именем уже существует"})



class WishlistTests(TestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.product = Product.objects.create(
            title='LG OLED',
            category=Category.objects.get(pk=1),
            price=100000,
            description='OLED 4K TV',
        )

    def test_get_empty_wishlist(self):
        response = self.client.get('/api/wishlist/', HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_add_to_wishlist(self):
        payload = {
            "product_id": self.product.id,
            "quantity": 2
        }
        response = self.client.post(
            '/api/wishlist/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['quantity'], 2)

    def test_remove_from_wishlist(self):
        WishlistItem.objects.create(user=self.user, product=self.product, quantity=1)
        response = self.client.delete(
            f'/api/wishlist/{self.product.id}',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}'
        )
        self.assertEqual(response.status_code, 200)

    def test_decrement_wishlist(self):
        WishlistItem.objects.create(user=self.user, product=self.product, quantity=2)
        response = self.client.delete(
            f'/api/wishlist/{self.product.id}/decrement',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}'
        )
        self.assertEqual(response.status_code, 200)
        item = WishlistItem.objects.get(user=self.user, product=self.product)
        self.assertEqual(item.quantity, 1)



class OrderTests(TestCase):
    fixtures = ['data.json']

    def setUp(self):
        self.user = User.objects.create_user(username='client', password='pass123')
        self.manager = User.objects.create_user(username='manager', password='pass123')
        managers_group = Group.objects.create(name="менеджеры")
        managers_group.user_set.add(self.manager)

        self.token = Token.objects.create(user=self.user)
        self.m_token = Token.objects.create(user=self.manager)

        self.status = OrderStatus.objects.create(name='Новый')
        self.product = Product.objects.get(pk=1)
        WishlistItem.objects.create(user=self.user, product=self.product, quantity=1)

    def test_create_order_from_wishlist(self):
        response = self.client.post(
            '/api/orders/',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Order.objects.filter(user=self.user).exists())

    def test_get_own_orders(self):
        order = Order.objects.create(user=self.user, status=self.status, total=10000)
        response = self.client.get(
            '/api/orders/my',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_orders_manager_access(self):
        response = self.client.get(
            '/api/orders/',
            HTTP_AUTHORIZATION=f'Bearer {self.m_token.key}')
        self.assertEqual(response.status_code, 200)

    def test_get_orders_no_permission(self):
        response = self.client.get(
            '/api/orders/',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}'
        )
        self.assertEqual(response.status_code, 403)

    def test_change_order_status(self):
        order = Order.objects.create(user=self.user, status=self.status, total=10000)
        new_status = OrderStatus.objects.create(name='Отправлен')
        response = self.client.put(
            f'/api/orders/{order.id}/status?status_id={new_status.id}',
            HTTP_AUTHORIZATION=f'Bearer {self.m_token.key}'
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, new_status)



class UserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='1234')
        self.manager = User.objects.create_user(username='manager1', password='1234')
        managers_group = Group.objects.create(name='менеджеры')
        managers_group.user_set.add(self.manager)

        self.token_user = Token.objects.create(user=self.user)
        self.token_mgr = Token.objects.create(user=self.manager)

    def test_get_users_manager(self):
        response = self.client.get(
            '/api/user/users/',
            HTTP_AUTHORIZATION=f'Bearer {self.token_mgr.key}'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_users_forbidden(self):
        response = self.client.get(
            '/api/user/users/',
            HTTP_AUTHORIZATION=f'Bearer {self.token_user.key}'
        )
        self.assertEqual(response.status_code, 403)


