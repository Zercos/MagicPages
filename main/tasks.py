from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_mail_to_customer_service(title, text, receivers):
    send_mail(title, text, settings.FROM_EMAIL, receivers)
