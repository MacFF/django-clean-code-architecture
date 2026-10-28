from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def user_register(*, email: str, password: str, first_name: str = "", last_name: str = "", **extra_fields):
    """
    Business Logic / Use Case: User registration and password hashing.
    """
    return User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        **extra_fields,
    )


def user_logout(*, user, refresh_token: str | None = None) -> None:
    """
    Business Logic / Use Case: User logout and immediate token revocation.
    """
    user.token_version += 1
    user.save(update_fields=["token_version"])

    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            pass

