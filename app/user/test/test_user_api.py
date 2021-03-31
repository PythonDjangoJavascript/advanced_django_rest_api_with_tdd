from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

# defining create here to access it from all classes bellow


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
        res = self.client.post(CREATE_USER_URL, payload)

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

    def test_create_token_for_user(self):
        """Test token is created for the user"""

        payload = {
            "email": "test@email.com",
            "password": "testPass123"
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Thes with in valid user and password"""

        create_user(email="test@email.com", password="testpassword")
        payload = {
            "email": "test@emal.com",
            "password": "wrongpass"
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test token is not created if user doesn't exist"""

        payload = {
            "email": "test@email.com",
            "password": "password"
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test email and password is must"""

        res = self.client.post(TOKEN_URL, {
            "email": "test@email.com",
            "password": ""
        })

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication required get update option"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test Api requests that require authentications"""

    def setUp(self):

        self.user = create_user(
            email="test@email.com",
            password="testpass",
            name="TestName"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        # this because bellow tests require authentication
        # using force_auth as we need to authenticate not login

    def test_retrieve_profile_success(self):
        """Test retriving profile for logged in user success"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "name": self.user.name,
            "email": self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        """Post is used for creating objects"""
        """because this option is olnly for update or PUT"""

        res = self.client.post(ME_URL, {})  # we are posting emptly input

        self.assertEqual(
            res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_success(self):
        """Test Updating the user profile for authenticated user"""

        payload = {
            "name": "New Name",
            "password": "updatedPassword"
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()  # as we just updated the user

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
