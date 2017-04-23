import unittest, re
from app import create_app, db
from app.models import Role, User
from flask import url_for

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue('Stranger' in response.get_data(as_text=True))
        
    def test_register_and_login(self):
        response = self.client.post(url_for('auth.register'), data={
            'email': 'admin@example.com',
            'user_name': 'Feng',
            'password1': 'katze',
            'password2': 'katze',
            'name': 'fzj',
            'location': 'Xuzhou'
        })
        self.assertTrue(b'Your account has been successfully created' in response.data)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(User.query.count() > 0)
        
        response = self.client.post(url_for('auth.login'), data={
            'email': 'admin@example.com',
            'password': 'katze'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search('Feng', data))
        self.assertTrue('Your account is unconfirmed' in data)
        
        user = User.query.filter_by(user_name='Feng').first()
        token = user.generate_confirm_token()
        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        self.assertTrue(b'Your account has been successfully actived' in response.data)
        
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        self.assertTrue(b'You have been logged out.' in response.data)