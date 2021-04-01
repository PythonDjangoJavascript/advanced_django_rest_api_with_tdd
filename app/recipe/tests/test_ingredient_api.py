from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientApiTests(TestCase):
    """Test the publickly avaliable ingrediesnts API"""

    def setUP(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test only logged in users can access this endpoint"""

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test Ingredients can be retrived by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@api.com",
            name="Ingredient"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingrents"""

        Ingredient.objects.create(user=self.user, name="Flour")
        Ingredient.objects.create(user=self.user, name="Salt")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_connected_user(self):
        """Test only ingredient are authenticated user are returened"""

        user2 = get_user_model().objects.create_user(
            email="second@user.com",
            password="secondpass"
        )
        Ingredient.objects.create(user=user2, name="Potato")

        ingredient = Ingredient.objects.create(user=self.user, name="Tomato")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)

    def test_create_ingredient_succcessful(self):
        """Test creating a new ingredient and added to the database"""

        payload = {"name": "Tomato"}
        self.client.post(INGREDIENTS_URL, payload)

        exist = Ingredient.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()
        self.assertTrue(exist)

    def test_create_invalid_ingredient(self):
        """Test if user post invalid ingredient"""

        payload = {"name": ""}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
