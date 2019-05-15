from unittest import TestCase
from server import app

from calculator import get_instructions

class FlaskTests(TestCase):

    def setUp(self):
        """Completed before each test"""

        self.client = app.test_client()
        app.config['TESTING'] = True


    def test_index(self):
        """Test the homepage is rendering correctly"""

        result = self.client.get('/')

        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Hello', result.data)


    def test_add_user(self):
        """Tests the add user form is rendered"""

        result = self.client.get('/adduser')

        self.assertEqual(result.status_code, 200)
        self.assertIn(b'Register as a user', result.data)


class FunctionTests(TestCase):
    """Tests for individual functions"""

    def test_get_instructions(self):
        """Test the get_instructions function"""

        self.assertDictEqual(get_instructions(10.2, 13.75, 7, 12, 20.5),{
            'amount_per_dose': 6.84,
            'total_amount': 95.78,
            'frequency_hrs': 12,
            'frequency_day': '2 times daily',
            'duration': 7
        })











