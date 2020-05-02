from django.test import TestCase

from main import models
from main.tests import factories


class TestModels(TestCase):
    def test_active_manager_works(self):
        factories.ProductFactory.create_batch(2, active=True)
        factories.ProductFactory(active=False)
        self.assertEqual(len(models.Product.objects.active()), 2)

    def test_get_by_natural_key(self):
        test_tag = factories.ProductTagFactory.create(slug='test_genre')
        factories.ProductTagFactory.create_batch(2)
        created_tag = models.ProductTag.objects.get_by_natural_key('test_genre')
        self.assertEqual(test_tag, created_tag)

    def test_creating_users(self):
        factories.UserFactory(email='test@mail.com', password='password')
        self.assertTrue(models.User.objects.filter(email='test@mail.com').exists())

    def test_create_user_address(self):
        user = factories.UserFactory()
        factories.AddressFactory(user=user)
        self.assertTrue(models.Address.objects.filter(user=user).exists())

    def test_basket_model(self):
        user = factories.UserFactory()
        basket = factories.BasketFactory(user=user)
        self.assertTrue(models.Basket.objects.filter(user=user).exists())
        self.assertTrue(basket.is_empty())

    def test_create_order(self):
        user = factories.UserFactory()
        basket = factories.BasketFactory(user=user)
        product1 = factories.ProductFactory()
        product2 = factories.ProductFactory()
        shipping_address = factories.AddressFactory(user=user)
        billing_address = factories.AddressFactory(user=user)
        models.BasketLine.objects.create(basket=basket, product=product1, quantity=2)
        models.BasketLine.objects.create(basket=basket, product=product2)
        basket.refresh_from_db()
        self.assertEqual(basket.count(), 3)
        with self.assertLogs("main.models", level='INFO') as cm:
            order = basket.create_order(shipping_address=shipping_address, billing_address=billing_address)
        self.assertGreaterEqual(len(cm.output), 1)
        order.refresh_from_db()
        self.assertEqual(order.user, user)
        self.assertEqual(order.billing_city, billing_address.city)
        self.assertEqual(order.shipping_address1, shipping_address.address1)
        self.assertEqual(order.lines.count(), 3)
        self.assertTrue(order.lines.filter(product=product1).exists())
