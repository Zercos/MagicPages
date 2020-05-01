import logging

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm, UsernameField
from django.core.mail import send_mail

from main import models
from main import tasks

logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    name = forms.CharField(label='Name', required=True, max_length=60)
    email = forms.EmailField(label='Email', required=True)
    content = forms.CharField(label='Message content', required=True, widget=forms.Textarea)

    def send_customer_service_email(self):
        logger.info(f'Sending email to customer service from {self.cleaned_data["email"]}')
        message = 'From: {}\n{}'.format(self.cleaned_data['name'], self.cleaned_data['content'])
        tasks.send_email.delay('Customer contact mail', message, [settings.CUSTOMER_SERVICE_EMAIL])


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm):
        model = models.User
        fields = ('email',)
        field_classes = {'email': UsernameField}

    def send_welcome_email(self):
        logger.info(f'Sending signup email for {self.cleaned_data["email"]}')
        message = 'Welcome to BookTime'
        send_mail(subject='BookTime welcome', message=message, from_email='site@booktime.domain',
                  recipient_list=(self.cleaned_data.get('email'),), fail_silently=True)


class AuthenticationForm(forms.Form):
    email = forms.EmailField(label='Emials')
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user = authenticate(request=self.request, email=email, password=password)
            if self.user is None:
                raise forms.ValidationError('Invalid email or password.')
            logger.info(f'Authenticate successfully {email}')
            return self.cleaned_data

    def get_user(self):
        return self.user


BasketLineFormSet = forms.inlineformset_factory(models.Basket, models.BasketLine, fields=('quantity',), extra=0)
