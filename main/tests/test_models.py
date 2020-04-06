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

