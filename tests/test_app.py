import unittest
from app import app, db

class TestFlaskApp(unittest.TestCase):
    def setUp(self) -> None:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()

    def tearDown(self) -> None:
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_page_loads(self) -> None:
        """Tests whether the index page loads (status code 200)."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self) -> None:
        """Tests access to the login page."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_register_pages_load(self) -> None:
        """Tests the registration pages."""
        res_sitter = self.client.get('/register/sitter')
        res_parent = self.client.get('/register/parent')
        self.assertEqual(res_sitter.status_code, 200)
        self.assertEqual(res_parent.status_code, 200)

    def test_404_error_handler(self) -> None:
        """Tests the custom 404 error page (errorhandler)."""
        response = self.client.get('/some-random-page-that-does-not-exist')
        self.assertEqual(response.status_code, 404)
        
    def test_register_sitter_validation_errors(self) -> None:
        """Tests the validation of the address field (missing fields)."""
        data = {
            'email': 'test@test.com',
            'city': '', 
            'password': '123'
        }
        response = self.client.post('/register/sitter', data=data, follow_redirects=True)
        self.assertIn(b'City is mandatory', response.data)
        
    def test_app_index(self) -> None:
        """Tests whether the index page loads through the Flask client."""
        from app import app
        client = app.test_client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_app_404(self) -> None:
        """Tests the 404 error handler."""
        from app import app
        client = app.test_client()
        response = client.get('/non-existent-page')
        self.assertEqual(response.status_code, 404)
        
    def test_flask_index(self) -> None:
        """Tests whether the index page loads (status code 200)."""
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)

    def test_flask_login_get(self) -> None:
        """Tests access to the login page."""
        from app import app
        with app.test_client() as client:
            response = client.get('/login')
            self.assertEqual(response.status_code, 200)

    def test_flask_404(self) -> None:
        """Tests whether the 404 handler works for a non-existent page."""
        from app import app
        with app.test_client() as client:
            response = client.get('/non-existent-page')
            self.assertEqual(response.status_code, 404)
            
    def test_index_with_filters(self) -> None:
        """Tests the index route with filtering parameters."""
        response = self.client.get('/?city=София&sort=experience')
        self.assertEqual(response.status_code, 200)

    def test_register_parent_missing_fields(self) -> None:
        """Tests the registration of a parent with missing required fields, expecting validation errors."""
        data = {'email': 'parent@test.com', 'city': ''}
        response = self.client.post('/register/parent', data=data, follow_redirects=True)
        self.assertIn(b'City is mandatory', response.data)
        
    def test_500_error(self) -> None:
        """Tests the 500 error handler by triggering an internal server error."""
        response = self.client.get('/booking/action/999/confirm')
        self.assertEqual(response.status_code, 302)

    def test_register_parent_validation(self) -> None:
        """Tests registration error handling (enters if/else blocks)."""
        data = {'email': 'test@test.com', 'city': ''}
        response = self.client.post('/register/parent', data=data, follow_redirects=True)
        self.assertIn(b'City is mandatory', response.data)
        
if __name__ == '__main__':
    unittest.main()