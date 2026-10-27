from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["token_version"] = user.token_version
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data = {
            "user": {
                "id": self.user.id,
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
            },
            "token": {
                "access": data["access"],
                "refresh": data["refresh"],
            },
        }
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    refresh_token = serializers.CharField(required=False, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["refresh"].required = False

    def validate(self, attrs):
        if not attrs.get("refresh") and attrs.get("refresh_token"):
            attrs["refresh"] = attrs["refresh_token"]
        if not attrs.get("refresh"):
            raise serializers.ValidationError({"refresh": ["This field is required."]})

        data = super().validate(attrs)
        data["token"] = {
            "access": data["access"],
            "refresh": data.get("refresh", attrs.get("refresh")),
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "password", "created_at", "updated_at"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        username = validated_data.pop("username", validated_data.get("email"))
        return User.objects.create_user(username=username, **validated_data)
