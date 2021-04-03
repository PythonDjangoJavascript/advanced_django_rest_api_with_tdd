import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Return recipe detail URL"""

    return reverse("recipe:recipe-detail", args=[recipe_id])


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""

    return reverse("recipe:recipe-upload-image", args=[recipe_id])


def sample_tag(user, name="Sample Tag"):
    """Create and return a sample tag"""

    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Ingredient"):
    """Create and return a sample Ingredient"""

    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        """Test retrieving a recipe detail"""

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating recipe"""

        payload = {
            "title": "Cholate cheese cake",
            "time_minutes": 20,
            "price": 600.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""

        tag1 = sample_tag(user=self.user, name="Vagan")
        tag2 = sample_tag(user=self.user, name="Dessert")
        payload = {
            "title": "Recipe with tags",
            "tags": [tag1.id, tag2.id],
            "time_minutes": 35,
            "price": 159.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""

        ingredient1 = sample_ingredient(user=self.user, name="cheeze")
        ingredient2 = sample_ingredient(user=self.user, name="Mutton")
        payload = {
            "title": "Chinese Burgur",
            "ingredients": [ingredient1.id, ingredient2.id],
            "time_minutes": 35,
            "price": 230
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    """Don't need to test bellow tests as we are using default updadte
    but I'm testing it just to practicce how to test updates"""

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        new_tag = sample_tag(user=self.user, name="new tag")

        payload = {
            "title": "Chicken tikka",
            "tags": [new_tag.id]
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])

        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with PUT"""

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            "title": "Sample Updated Recipe",
            "time_minutes": 25,
            "price": 50.00
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.time_minutes, payload["time_minutes"])
        self.assertEqual(recipe.price, payload["price"])

        tags = recipe.tags.all()

        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):
    """Test image upload API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="image@api.com",
            password="uploadimage"
        )

        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    # it runs after every method
    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""

        url = image_upload_url(self.recipe.id)

        # namedTemporaryFlie create temp file in a random location
        # and suffix is the extention of that file
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            # setting seek 0 so next time image will be read from beggining
            ntf.seek(0)

            # formate is multipart as it will contain data(image) file
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""

        url = image_upload_url(self.recipe.id)
        res = self.client.post(
            url, {"image": "Not Image"}, formate="murtipart"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """Test retieving recipes with specific tags"""

        recipe2 = sample_recipe(user=self.user, title="Chinese Veg Curry")
        recipe3 = sample_recipe(user=self.user, title="Thai Fish Curry")
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Sea food")
        recipe2.tags.add(tag1)
        recipe3.tags.add(tag2)

        res = self.client.get(
            RECIPES_URL,
            {"tags": f"{tag1.id},{tag2.id}"}
        )

        serializer1 = RecipeSerializer(self.recipe)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """Test retrieving recipes with sepcific ingredients"""

        recipe2 = sample_recipe(user=self.user, title="Chocklet Tost")
        recipe3 = sample_recipe(user=self.user, title="Chicken Burger")
        ingredient1 = sample_ingredient(user=self.user, name="Biskits")
        ingredient2 = sample_ingredient(user=self.user, name="Chicken")
        recipe2.ingredients.add(ingredient1)
        recipe3.ingredients.add(ingredient2)

        res = self.client.get(
            RECIPES_URL,
            {"ingredients": f"{ingredient1.id},{ingredient2.id}"}
        )

        serializer1 = RecipeSerializer(self.recipe)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)
