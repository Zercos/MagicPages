import logging
from functools import reduce

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from django.db import models

logger = logging.getLogger(__name__)


class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)


class ProductTagManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class ProductTag(models.Model):
    objects = ProductTagManager()

    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.slug


class Product(models.Model):
    objects = ActiveManager()

    tags = models.ManyToManyField(ProductTag, blank=True)
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(max_length=48)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product-images')
    thumbnail = models.ImageField(upload_to='product-thumbnails', null=True)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email=email, password=password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Super user must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Super user must have is_superuser=True')
        return self._create_user(email=email, password=password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    @property
    def is_employee(self):
        return self.is_active and (self.is_superuser or self.is_staff and self.groups.filter(name='Employees').exists())

    @property
    def is_dispatcher(self):
        return self.is_active and (
                self.is_superuser or self.is_staff and self.groups.filter(name='Dispatchers').exists())


class Address(models.Model):
    COUNTRIES = (('pl', 'Poland'), ('ua', 'Ukraine'), ('us', 'USA'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=60)
    address1 = models.CharField('Address line 1', max_length=120)
    address2 = models.CharField('Address line 2', max_length=120, null=True, blank=True)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=60)
    country = models.CharField(max_length=5, choices=COUNTRIES)

    def __str__(self):
        if not self.name:
            return super().__str__()
        return ', '.join([self.name, self.address1, self.address2 or '', self.zip_code, self.city, self.country])


class Basket(models.Model):
    OPEN = 10
    SUBMITTED = 20
    STATUSES = ((OPEN, 'Open'), (SUBMITTED, 'Submitted'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=OPEN)

    def is_empty(self):
        return self.basketline_set.all().count() == 0

    def count(self):
        return sum(i.quantity for i in self.basketline_set.all())

    def create_order(self, billing_address, shipping_address):
        if not self.user:
            raise Exception('Cannot create order without user.')
        logger.info((f'Creating order for basket={self.id}, billing_address={billing_address.id}, '
                     f'shipping_address={shipping_address.id}'))
        order_data = {
            'user': self.user,
            'billing_name': billing_address.name,
            'billing_address1': billing_address.address1,
            'billing_address2': billing_address.address2,
            'billing_zip_code': billing_address.zip_code,
            'billing_city': billing_address.city,
            'billing_country': billing_address.country,
            'shipping_name': shipping_address.name,
            'shipping_address1': shipping_address.address1,
            'shipping_address2': shipping_address.address2,
            'shipping_zip_code': shipping_address.zip_code,
            'shipping_city': shipping_address.city,
            'shipping_country': shipping_address.country,
        }
        order = Order.objects.create(**order_data)
        orderline_number = 0
        for line in self.basketline_set.all():
            for item in range(line.quantity):
                OrderLine.objects.create(order=order, product=line.product)
                orderline_number += 1
        logger.info(f'Created order: {order.id}, with lines_count={orderline_number}')
        self.status = Basket.SUBMITTED
        self.save()
        return order

    @property
    def full_price(self):
        return reduce(lambda accum, line: accum + line.sum_price, self.basketline_set.all(), 0)


class BasketLine(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    @property
    def sum_price(self):
        return reduce(lambda accum, _: accum + self.product.price, range(self.quantity), 0)


class Order(models.Model):
    NEW = 10
    PAID = 20
    DONE = 30
    STATUSES = ((NEW, 'New'), (PAID, 'Paid'), (DONE, 'Done'))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=NEW)

    billing_name = models.CharField(max_length=60)
    billing_address1 = models.CharField('Address line 1', max_length=120)
    billing_address2 = models.CharField('Address line 2', max_length=120, null=True, blank=True)
    billing_zip_code = models.CharField(max_length=20)
    billing_city = models.CharField(max_length=60)
    billing_country = models.CharField(max_length=5)

    shipping_name = models.CharField(max_length=60)
    shipping_address1 = models.CharField('Address line 1', max_length=120)
    shipping_address2 = models.CharField('Address line 2', max_length=120, null=True, blank=True)
    shipping_zip_code = models.CharField(max_length=20)
    shipping_city = models.CharField(max_length=60)
    shipping_country = models.CharField(max_length=5)

    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)


class OrderLine(models.Model):
    NEW = 10
    PROCESSING = 20
    SENT = 30
    CANCELLED = 40
    STATUSES = ((NEW, 'New'), (PROCESSING, 'Processing'), (SENT, 'Sent'), (CANCELLED, 'Cancelled'))

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUSES, default=NEW)
