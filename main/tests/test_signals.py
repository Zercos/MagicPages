from decimal import Decimal

from django.core.files.images import ImageFile
from django.test import TestCase

from main import models


class TestSignal(TestCase):
    def test_thumbnails_are_generated_on_save(self):
        product = models.Product(name='Shining', price=Decimal('10.00'))
        product.save()

        with open('main/fixtures/shining.jpeg', 'rb') as f:
            image = models.ProductImage(product=product, image=ImageFile(f, name='shining.jpeg'))
            with self.assertLogs('main', level='INFO') as cm:
                image.save()
        self.assertGreaterEqual(len(cm.output), 1)
        image.refresh_from_db()
        with open('media/product-thumbnails/shining.jpeg', 'rb') as f:
            expected_content = f.read()
            assert image.thumbnail.read() == expected_content
        image.thumbnail.delete(save=False)
        image.image.delete(save=False)
