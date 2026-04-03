from django.test import TestCase

# Create your tests here.
from .models import User
from .serializers import LoginSerializer


class UserModelTests(TestCase):
    def test_superuser_is_saved_with_admin_role(self):
        user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin1',
            password='Admin@12345',
        )

        self.assertEqual(user.role, 'admin')


class LoginSerializerTests(TestCase):
    def test_login_serializer_authenticates_with_email_and_password(self):
        User.objects.create_user(
            email='customer@example.com',
            username='customer1',
            password='Customer@12345',
            role='customer',
        )

        serializer = LoginSerializer(
            data={'email': 'customer@example.com', 'password': 'Customer@12345'}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
