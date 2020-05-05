from decimal import Decimal
from unittest.mock import patch

from django.contrib import auth
from django.test.testcases import TestCase
from django.urls import reverse

from main import forms
from main.models import Product, User, Address, Basket, BasketLine
from main.tests.factories import UserFactory, AddressFactory, ProductFactory, BasketFactory


class TestViews(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse('main:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Magic Pages')

    def test_about_us_page(self):
        response = self.client.get(reverse('main:about_us'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About us')

    def test_contact_us_page(self):
        response = self.client.get(reverse('main:contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact us')

    def test_product_page_active(self):
        Product.objects.create(name='Tom', price=Decimal(10.00), slug='tom')
        Product.objects.create(name='Sor', price=Decimal(11.00), slug='sor')

        response = self.client.get(reverse('main:products', kwargs={'tag': 'all'}))
        products = Product.objects.active().order_by('name')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(products), list(response.context['product_list']))

    def test_product_page_tag(self):
        tom = Product.objects.create(name='Tom', price=Decimal(10.00), slug='tom')
        Product.objects.create(name='Sor', price=Decimal(11.00), slug='sor')
        tom.tags.create(name='Drama', slug='drama')

        response = self.client.get(reverse('main:products', kwargs={'tag': 'drama'}))
        products = Product.objects.active().filter(tags__slug='drama').order_by('name')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(products), list(response.context['product_list']))

    def test_product_detail_page(self):
        book = Product.objects.create(name='Shine', price=Decimal(10), slug='shining')

        response = self.client.get(reverse('main:product', kwargs={'slug': book.slug}))

        self.assertEqual('shining', book.slug)
        self.assertEqual(200, response.status_code)
        self.assertEqual(book, response.context['product'])

    def test_get_registration_page(self):
        response = self.client.get(reverse('main:signup'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign up')
        self.assertTemplateUsed(response, 'signup.html')
        self.assertIsInstance(response.context['form'], forms.UserCreationForm)

    def test_user_signup_work(self):
        post_data = {
            'email': 'test@mail.com',
            'password1': 'somepassword',
            'password2': 'somepassword'
        }
        with patch.object(forms.UserCreationForm, 'send_welcome_email') as mock_send:
            response = self.client.post(reverse('main:signup'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='test@mail.com').exists())
        self.assertTrue(auth.get_user(self.client).is_authenticated)
        mock_send.assert_called()

    def test_get_login_page(self):
        response = self.client.get(reverse('main:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIsInstance(response.context['form'], forms.AuthenticationForm)

    def test_user_authentication(self):
        user = UserFactory(email='user@mail.com')
        credentials = dict(email='user@mail.com', password='password')
        response = self.client.post(reverse('main:login'), credentials)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(auth.get_user(self.client).is_authenticated)

    def test_get_address_list_for_user(self):
        user1 = UserFactory()
        user2 = UserFactory()
        address1 = AddressFactory(user=user1)
        address2 = AddressFactory(user=user2)
        self.client.force_login(user1)
        response = self.client.get(reverse('main:address_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/address_list.html')
        address_list = Address.objects.filter(user=user1)
        self.assertEqual(list(response.context['address_list']), list(address_list))

    def test_create_address(self):
        user = UserFactory()
        post_data = {
            'name': 'some',
            'address1': 'addr1',
            'city': 'Lublin',
            'zip_code': '12233',
            'country': 'pl'
        }
        self.client.force_login(user)
        response = self.client.post(reverse('main:address_create'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Address.objects.filter(user=user))
        self.assertEqual(Address.objects.get(user=user).city, 'Lublin')

    def test_update_address(self):
        user = UserFactory()
        address = AddressFactory(user=user)
        self.client.force_login(user)
        update_data = {
            'name': address.name,
            'address1': address.address1,
            'address2': address.address2,
            'country': address.country,
            'zip_code': address.zip_code,
            'city': 'Warsaw'
        }
        response = self.client.post(reverse('main:address_update', kwargs={'pk': address.id}), update_data)
        address.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(address.city, 'Warsaw')

    def test_delete_user_address(self):
        user = UserFactory()
        self.client.force_login(user)
        address = AddressFactory(user=user)
        self.assertTrue(Address.objects.filter(user=user).exists())
        response = self.client.post(reverse('main:address_delete', kwargs={'pk': address.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Address.objects.filter(user=user).exists())

    def test_add_to_basket(self):
        user = UserFactory()
        product1 = ProductFactory()
        product2 = ProductFactory()
        self.client.force_login(user)
        self.client.get(reverse('main:add_to_basket'), {'product_id': product1.id})
        self.assertTrue(Basket.objects.filter(user=user).exists())
        self.client.get(reverse('main:add_to_basket'), {'product_id': product1.id})
        self.client.get(reverse('main:add_to_basket'), {'product_id': product2.id})
        self.assertEqual(Basket.objects.get(user=user).count(), 3)
        self.assertTrue(BasketLine.objects.filter(product=product2).exists())
        self.assertEqual(BasketLine.objects.filter(basket__user=user).count(), 2)

    def test_merge_basket_on_login(self):
        user = UserFactory(email='user1@mail.com')
        product1 = ProductFactory()
        product2 = ProductFactory()
        self.client.get(reverse('main:add_to_basket'), {'product_id': product2.id})
        self.assertTrue(BasketLine.objects.filter(product=product2).exists())
        credentials = dict(email='user@mail.com', password='password')
        self.client.post(reverse('main:login'), {'email': 'user1@mail.com', 'password': 'password'})
        self.assertTrue(auth.get_user(self.client).is_authenticated)
        self.assertTrue(Basket.objects.filter(user=user).exists())
        self.client.get(reverse('main:add_to_basket'), {'product_id': product1.id})
        self.assertEqual(Basket.objects.get(user=user).count(), 2)
        self.assertTrue(BasketLine.objects.filter(product=product2).exists())
        self.assertEqual(BasketLine.objects.get(product=product1).quantity, 1)
