from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ("id",)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for an ingredient object"""

    class Meta:
        model = Ingredient
        fields = ("id", "name",)
        read_only_fields = ("id",)


class RecipeSerializer(serializers.ModelSerializer):
    """Seerialize a recipe"""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            "id", "title", "tags", "ingredients", "time_minutes",
            "price", "link"
        )
        read_only_fields = ("id",)


class RecipeDetailSerializer(RecipeSerializer):
    """Serialize a recipe detail"""

    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
