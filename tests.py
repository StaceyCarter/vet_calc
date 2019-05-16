from unittest import TestCase
from server import app

from calculator import get_instructions, get_num_tablets_per_dose

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

        self.assertDictEqual(get_instructions(10.2, 13.75, 20.5, 7, 12, 'liq'),{
            'amount_per_dose': 6.84,
            'total_amount': 95.78,
            'frequency_hrs': 12,
            'frequency_day': '2 times daily',
            'duration': 7,
            'form': 'liq'
        })

        self.assertDictEqual(get_instructions(50, 2.5, 100, 14, 8, 'tab', 4),{
            'amount_per_dose': 1.25,
            'total_amount': 52.5,
            'frequency_hrs': 8,
            'frequency_day': '3 times daily',
            'duration': 14,
            'form': 'tab'
        })

        self.assertDictEqual(get_instructions(50, 2.5, 100, 14, 8, 'tab', 2), {
            'amount_per_dose': 1.0,
            'total_amount': 42,
            'frequency_hrs': 8,
            'frequency_day': '3 times daily',
            'duration': 14,
            'form': 'tab'
        })

    def test_calc_num_tabs_per_dose(self):
        """Tests the rounding function to calculate the number of tablets per dose."""

        self.assertEqual(get_num_tablets_per_dose(120, 100), 1.0)
        self.assertEqual(get_num_tablets_per_dose(600, 500), 1.0)
        self.assertEqual(get_num_tablets_per_dose(600, 500, 4), 1.25)
        self.assertEqual(get_num_tablets_per_dose(280, 100, 2), 3.0)













