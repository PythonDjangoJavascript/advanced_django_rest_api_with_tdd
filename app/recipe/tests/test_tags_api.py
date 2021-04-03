from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer
import user


TAGS_URL = reverse("recipe:tag-list")


class PublicTagsApiTests(TestCase):
    """Test the publicky available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user  tags API"""

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            email="test@tags.com",
            password="passwordtags"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retirive_tags(self):
        """Test retriving tags success"""

        Tag.objects.create(user=self.user, name="Vegitable")
        Tag.objects.create(user=self.user, name="Non-Veg")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for only authenticated user"""

        user_two = get_user_model().objects.create_user(
            email="second@user.com",
            password="secondpass"
        )
        Tag.objects.create(user=user_two, name="Fruty")
        tag = Tag.objects.create(user=self.user, name="Junk")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag succesful"""

        payload = {"name": "simple"}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()

        self.assertTrue(exists)

    def test_crate_invalid_tag(self):
        """Test creating a new tag with invalid payload"""

        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""

        tag1 = Tag.objects.create(
            user=self.user,
            name="Breakfast"
        )
        tag2 = Tag.objects.create(
            user=self.user,
            name="Lunch"
        )
        recipe = Recipe.objects.create(
            title="Fish curry",
            time_minutes=20,
            price=280.00,
            user=self.user
        )
        recipe.tags.add(tag2)

        res = self.client.get(TAGS_URL, {"assigned_only", 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)

    def test_retieve_tags_assigned_to_unique(self):
        """Test filtering tags by assinged returns unique items"""
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        Tag.objects.create(user=self.user, name="Lunch")
        recipe1 = Recipe.objects.create(
            user=self.user,
            title="Cheese cake",
            time_minutes=10,
            price=60.00
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            user=self.user,
            title="Porridge",
            time_minutes=3,
            price=30.00,
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only", 1})

        self.assertEqual(len(res.data), 1)
