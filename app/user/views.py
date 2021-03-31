from rest_framework import generics

from user.serializers import UserSerializser


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializser
