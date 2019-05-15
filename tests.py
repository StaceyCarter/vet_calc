from unittest import TestCase
from server import app

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


