from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

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
                "min_length": 5,
                "style": {"input_type": "password"}
            }
        }

    def create(self, validated_data):
        """we are overriding default create to use our
            encripted password method"""

        return get_user_model().objects.create_user(**validated_data)

    # def update(self, instance, validated_data):
    #     return super().update(instance, validated_data)

    # Here instance is the model instance
    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""

        password = validated_data.pop("password", None)  # None is for default
        # for other data we will use default update as
        #  they don't requre encryption
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authenticaiton object"""

    email = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False  # as Sometimes django can trim space by default
    )

    # this method validate inputs
    def validate(self, attrs):
        """Validate input and authenticate user"""
        """Here attrs(atributes) return above defined data given by user"""

        email = attrs.get("email")
        password = attrs.get("password")

        # Django authenticate method generate tocken
        # from valid username and pass
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if not user:
            # it is good practice to translate message so make it convinient
            # for different language
            msg = _("Unable to authenticate with provided content")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
