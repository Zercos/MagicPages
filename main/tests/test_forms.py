from django.core import mail
from django.test import TestCase
from main.tests import MockSendContactEmail

from main.forms import ContactForm


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
        self.assertEqual(self.send_mail_to_customer_service_mock.delay.call_count, 1)
        self.assertGreaterEqual(len(cm.output), 1)

    def test_invalid_contact_form(self):
        form = ContactForm({
            'name': 'Kali Rose',
            'content': 'Hi'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(self.send_mail_to_customer_service_mock.delay.call_count, 0)
