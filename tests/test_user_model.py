from app import user_datastore

from test_basics import BasicTestCase


class UserModel(BasicTestCase):
    """
    Testing the user model
    """
    def test_add_user(self):
        """
        Test if we can create a user and return it
        """
        user_datastore.create_user(email='test@example.com',
                                   password='password',
                                   username='Test',
                                   active=True)
        self.assertTrue(True)
        user = user_datastore.get_user('test@example.com')
        self.assertIn('Test', str(user))

    def test_add_role(self):
        """
        Test if we can create a role and return it
        """
        user_datastore.create_role(name='admin',
                                   description='Administrator')
        admin = user_datastore.find_role('admin')
        self.assertIn('Administrator', str(admin))
        user_datastore.create_role(name='user')
        user = user_datastore.find_role('user')
        self.assertIn('user', str(user))
