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
