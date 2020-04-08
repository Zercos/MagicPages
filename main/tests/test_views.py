from decimal import Decimal

from django.test.testcases import TestCase
from django.urls import reverse

from main.models import Product


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
