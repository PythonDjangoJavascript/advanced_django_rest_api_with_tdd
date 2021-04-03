from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch

from core import models


def sample_user(email="test@email.com", password="testPass"):
    """Create sample user to be accessable to all tests"""

    return get_user_model().objects.create_user(email, password)


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

    def test_tag_str(self):
        """Test tag created successfully and check that by its str method"""

        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Spicy"
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test ingredient created successfully by its str method"""

        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Potato"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test recipe model working by testing its str method"""

        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Burger",
            time_minutes=4,
            price=350.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch("uuid.uuid4")
    def test_recipe_filename_uuid(self, mock_uuid):
        """Test taht image is saved in correct loaction with generated name"""

        uuid = "test_uuid"
        mock_uuid.return_value = uuid
        file_path = models.reciepe_image_file_path(None, "Myimage.jpg")

        exp_path = f"uploads/recipe/{uuid}.jpg"
        self.assertEqual(file_path, exp_path)


#######
