from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


RECIPES_URL = reverse("recipe:recipe-list")


def sample_recipe(user, **params):
    """Create and return a sample recipe"""

    defaults = {
        "title": "Sample Recipe",
        "time_minutes": 10,
        "price": 100.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test Unauthorized recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        """Test only logged in users can access"""

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test Authorized recipe API tests"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="recipe@test.com",
            password="recipepass"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """Test retrieving list of recipes"""

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        # serializer ordering by id but don't konw why
        recipes = Recipe.objects.all().order_by("id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_owner_user(self):
        """Test Retrieving recipes for owner user"""

        user2 = get_user_model().objects.create_user(
            email="second@user.com",
            password="testuser"
        )
        sample_recipe(user=user2)
        sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
