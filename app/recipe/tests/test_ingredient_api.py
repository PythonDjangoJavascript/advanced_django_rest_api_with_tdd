from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

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

    def test_retreve_ingredients_assinged_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""

        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name="Apple"
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name="Turkey"
        )
        recipe = Recipe.objects.create(
            user=self.user,
            title="Apple Crumble",
            time_minutes=5,
            price=100.00
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retieve_ingredient_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""

        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Egg"
        )
        Ingredient.objects.create(
            user=self.user,
            name="Cheese"
        )
        recipe1 = Recipe.objects.create(
            title="Eggs bendict",
            time_minutes=30,
            price=80.00,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title="Egg Toast",
            time_minutes=15,
            price=50.00,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
