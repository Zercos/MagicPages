from django.test.testcases import TestCase
from django.urls import reverse


class TestViews(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse('main:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Magic Pages')
