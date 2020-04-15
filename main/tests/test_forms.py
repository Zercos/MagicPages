from django.core import mail
from django.test import TestCase

from main.forms import ContactForm, UserCreationForm
from main.tests import MockSendContactEmail


class TestForms(MockSendContactEmail, TestCase):
    def test_valid_contact_form(self):
        form = ContactForm({
            'name': 'Kimmy Granger',
            'email': 'kimm@mail.com',
            'content': 'How are you?'
        })
        self.assertTrue(form.is_valid())
        with self.assertLogs('main.forms', level='INFO') as cm:
            form.send_customer_service_email()
        self.assertEqual(self.send_mail_celery_mock.delay.call_count, 1)
        self.assertGreaterEqual(len(cm.output), 1)

    def test_invalid_contact_form(self):
        form = ContactForm({
            'name': 'Kali Rose',
            'content': 'Hi'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(self.send_mail_celery_mock.delay.call_count, 0)

    def test_user_creation_form(self):
        form = UserCreationForm({'email': 'test@mail.com', 'password1': 'somepassword', 'password2': 'somepassword'})
        self.assertTrue(form.is_valid())
        with self.assertLogs('main.forms', level='INFO') as cm:
            form.send_welcome_email()
        self.assertGreaterEqual(len(cm.output), 1)
        self.assertEqual(len(mail.outbox), 1)
