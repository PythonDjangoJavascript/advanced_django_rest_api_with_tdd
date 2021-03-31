from rest_framework import generics
from rest_framework import authentication
from rest_framework import permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializser
from user.serializers import AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializser


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for the user"""

    serializer_class = AuthTokenSerializer

    # renderer_classes to render browseble view
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Mange the authenticatited user"""

    serializer_class = UserSerializser
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Related object (here user)"""
        return self.request.user
