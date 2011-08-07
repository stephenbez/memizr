import unittest
from django.test.client import Client

class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_review_should_not_return_error(self):
        register_response = self.client.post('/accounts/register/', {'username': 'john', 'email': 'john@example.com', 'password1': 'abcd', 'password2': 'abcd'})

        self.assertEqual(302, register_response.status_code)

        review_response = self.client.get('/review/')

        self.assertEqual(200, review_response.status_code)
