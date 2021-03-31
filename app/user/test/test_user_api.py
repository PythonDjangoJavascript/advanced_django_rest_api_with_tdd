from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")


def create_user(**params):
    """Helper function to create new user"""

    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the user API which don't require login"""

    def setUp(self):
        """Setup method for makigin its attribute available to every method"""

        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test create api with valid payload is successful"""

        payload = {
            "email": "test@api.com",
            "password": "tesapipass",
            "name": "Test Api User"
        }
        res = self.client.post(CREATE_USER_URL, payload)
        user = get_user_model().objects.get(**res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload["password"]))
        # get response should not send user's password data
        self.assertNotIn("password", res.data)

    def test_user_duplicate(self):
        """test creating user already exits fails"""

        payload = {
            "email": "test@api.com",
            "password": "testapipasswore",
            "name": "Api User"
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, **payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """test 5 car password condition works"""
        """Then check whether the user is added or not"""
        payload = {
            "email": "test@api.com",
            "password": "pas",
            "name": "Name"
        }
        res = self.client.post(CREATE_USER_URL, **payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # The user doesn't exsit in our database as post wasn't successful
        user_exist = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()

        self.assertFalse(user_exist)
