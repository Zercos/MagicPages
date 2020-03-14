import logging

from django import forms
from django.conf import settings

from main import tasks

logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    name = forms.CharField(label='Name', required=True, max_length=60)
    email = forms.EmailField(label='Email', required=True)
    content = forms.CharField(label='Message content', required=True, widget=forms.Textarea)

    def send_customer_service_email(self):
        logger.info(f'Sending email to customer service from {self.cleaned_data["email"]}')
        message = 'From: {}\n{}'.format(self.cleaned_data['name'], self.cleaned_data['content'])
        tasks.send_mail_to_customer_service.delay('Customer contact mail', message, [settings.CUSTOMER_SERVICE_EMAIL])
