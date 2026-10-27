from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class VersionedJWTAuthentication(JWTAuthentication):
    """
    Checks token_version in the JWT payload against user.token_version.
    Raises 401 if the token was revoked (e.g. user logged out).
    """

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        token_version = validated_token.get("token_version")

        if token_version is None or token_version != user.token_version:
            raise AuthenticationFailed("User token has been revoked or expired.")

        return user


class VersionedJWTScheme(OpenApiAuthenticationExtension):
    target_class = "apps.users.authentication.VersionedJWTAuthentication"
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        return {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
