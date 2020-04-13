from decimal import Decimal
from unittest.mock import patch

from django.contrib import auth
from django.test.testcases import TestCase
from django.urls import reverse

from main import forms
from main.models import Product, User


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
