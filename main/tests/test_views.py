from django.test.testcases import TestCase
from django.urls import reverse


class TestViews(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse('main:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Magic Pages')

    def test_about_us_page(self):
        response = self.client.get(reverse('main:about_us'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About us')

    def test_contact_us_page(self):
        response = self.client.get(reverse('main:contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact us')
