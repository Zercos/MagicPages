import logging
from io import BytesIO

from PIL import Image
from django.contrib.auth.signals import user_logged_in
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import ProductImage, Basket, OrderLine, Order

from main.models import ProductImage, Basket

THUMBNAIL_SIZE = (300, 300)
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ProductImage)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info('Generating thumbnail for product %d', instance.product.id)
    image = Image.open(instance.image)
    image = image.convert('RGB')
    image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

    temp_thumb = BytesIO()
    image.save(temp_thumb, 'JPEG')
    temp_thumb.seek(0)

    # set save=False, otherwise it will run in an infinite loop
    instance.thumbnail.save(
        instance.image.name,
        ContentFile(temp_thumb.read()),
        save=False,
    )
    temp_thumb.close()


@receiver(user_logged_in)
def merge_basket_if_found(sender, user, request, **kwargs):
    anonymous_basket = getattr(request, 'basket', None)
    if anonymous_basket:
        try:
            logged_basket = Basket.objects.get(user=user, status=Basket.OPEN)
            for line in anonymous_basket.basketline_set.all():
                line.basket = logged_basket
                line.save()
            anonymous_basket.delete()
            request.basket = logged_basket
            logger.info(f'Merget basket to id {logged_basket.id}')
        except Basket.DoesNotExist:
            anonymous_basket.user = user
            anonymous_basket.save()
            logger.info(f'Assigned user to basket {anonymous_basket.id}')

@receiver(post_save, sender=OrderLine)
def orderline_to_order_status(sender, instance, **kwargs):
    if not instance.order.lines.filter(status__lt=OrderLine. SENT).exists():
        logger.info(
            "All lines for order %d have been processed. Marking as done.",
            instance.order.id,
        )
        instance.order.status = Order.DONE
        instance.order.save()
