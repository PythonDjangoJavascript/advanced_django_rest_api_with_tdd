from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag

from recipe import serializers


# We are useing mixitn to specify which module we are gonna use
# As we don't need all mixins which comes by default
class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Mangae tags in database"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # Useing get_querey as we don't wanna use default which will not filter
    # Any object and will retrun all
    def get_queryset(self):
        """Return objects for the current authenticated user only"""

        return self.queryset.filter(user=self.request.user).order_by("-name")

    # overriding create to set the user to authenticated user
    def perform_create(self, serializer):
        """Create a new ingreadient"""

        serializer.save(user=self.request.user)
