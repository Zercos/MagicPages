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


class UserFactory(factory.DjangoModelFactory):
    email = factory.Sequence(lambda x: f'user{x}@mail.com')
    password = factory.PostGenerationMethodCall('set_password', 'password')
    first_name = factory.faker.Faker('first_name')
    last_name = factory.faker.Faker('last_name')

    class Meta:
        model = models.User


class AddressFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    name = factory.fuzzy.FuzzyText(length=12)
    address1 = factory.faker.Faker('address')
    address2 = factory.faker.Faker('address')
    zip_code = factory.faker.Faker('postcode')
    city = factory.faker.Faker('city')
    country = factory.fuzzy.FuzzyChoice(models.Address.COUNTRIES, getter=lambda c: c[0])

    class Meta:
        model = models.Address


class BasketFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Basket
