from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


# We are useing mixitn to specify which module we are gonna use
# As we don't need all mixins which comes by default
# class TagViewSet(viewsets.GenericViewSet,
#                  mixins.ListModelMixin,
#                  mixins.CreateModelMixin):
#     """Mangae tags in database"""

#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     queryset = Tag.objects.all()
#     serializer_class = serializers.TagSerializer

#     # Useing get_querey as we don't wanna use default which will not filter
#     # Any object and will retrun all
#     def get_queryset(self):
#         """Return objects for the current authenticated user only"""

#         return self.queryset.filter(user=self.request.user).order_by("-name")

#     # overriding create to set the user to authenticated user
#     def perform_create(self, serializer):
#         """Create a new ingreadient"""

#         serializer.save(user=self.request.user)


# class IngredientViewSet(viewsets.GenericViewSet,
#                         mixins.ListModelMixin,
#                         mixins.CreateModelMixin):
#     """Manage ingredient in the database"""

#     authentication_classes = (TokenAuthentication, )
#     permission_classes = (IsAuthenticated, )
#     queryset = Ingredient.objects.all()
#     serializer_class = serializers.IngredientSerializer

#     def get_queryset(self):
#         """Return objets for the current authenticated user only"""

#         return self.queryset.filter(user=self.request.user).order_by("-name")

#     def perform_create(self, serializer):
#         """Create a new ingredient and add it to the database"""

#         serializer.save(user=self.request.user)


# We are useing mixitn to specify which module we are gonna use
# As we don't need all mixins which comes by default
class BaseRecipeAttrViewSets(viewsets.GenericViewSet,
                             mixins.ListModelMixin,
                             mixins.CreateModelMixin):
    """Base Viewset for user woned recipe attributes"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    # Useing get_querey as we don't wanna use default which will not filter
    # Any object and will retrun all
    def get_queryset(self):
        """Return objects for the current authenticated user only"""

        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        """Create a new object to the database"""

        # overriding create to set the user to authenticated user
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSets):
    """Mange tags in the databse"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSets):
    """Manage Ingredients in the database"""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    # Here we are using modelviewset as we want to use all
    #  create,update,delete.. methods
    """Manage recipes in the database"""

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Retireve the recipe for the authenticated user"""

        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer clss"""

        if self.action == "retrieve":
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        """Modelserializer know how to create new object to our model as we
        already defined the model here we just need to set the authenticated
        user to perform the create function"""

        serializer.save(user=self.request.user)
