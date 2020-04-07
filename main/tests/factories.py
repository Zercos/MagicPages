import factory.fuzzy

from main import models


class ProductTagFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda x: f'Genre {x}')
    slug = factory.Sequence(lambda x: f'genre_{x}')
    description = factory.fuzzy.FuzzyText()

    class Meta:
        model = models.ProductTag


class ProductFactory(factory.DjangoModelFactory):
    price = factory.fuzzy.FuzzyDecimal(1.0, 1000.0)
    tags = factory.RelatedFactory(ProductTagFactory)
    name = factory.Sequence(lambda x: f'Book {x}')
    description = factory.fuzzy.FuzzyText()
    slug = factory.Sequence(lambda x: f'book_{x}')

    class Meta:
        model = models.Product
