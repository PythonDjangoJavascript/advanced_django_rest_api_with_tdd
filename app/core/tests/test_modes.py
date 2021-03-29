from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    """Tests our custom user models"""

    def test_create_user_successful(self):
        """Test creating user method working and user don't
         have super permissions"""

        email = "test@email.com"
        password = "testapss123"
        name = "testuser"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.name, name)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_user_email_normalized(self):
        """Test users email normalized method working"""

        email = "test@EmAIl.cOm"
        user = get_user_model().objects.create_user(
            email=email,
            password="testapss123",
            name="testuser"
        )

        self.assertEqual(user.email, email.lower())

    def test_non_emai_raise_value_error(self):
        """Test if user don't provide email address"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                name="Name",
                password="Password"
            )

    def test_admin_user_has_permissions(self):
        """test superuser function give the is staff and super permissions"""

        user = get_user_model().objects.create_superuser(
            email="super@user.com",
            password="superuserpass"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
