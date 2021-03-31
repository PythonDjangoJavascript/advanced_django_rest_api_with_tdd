from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializser(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        """Meta class defins the models and its attributes"""

        model = get_user_model()
        fields = ("email", "password", "name")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5
            }
        }

    def create(self, validated_data):
        """we are overriding default create to use our
            encripted password method"""

        return get_user_model().objects.create_user(**validated_data)
