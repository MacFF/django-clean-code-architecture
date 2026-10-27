from django.db import transaction
from django.shortcuts import render

from django.contrib.auth import get_user_model
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed

from apps.users.serializers import UserSerializer

User = get_user_model()


class CustomLoginView(TokenObtainPairView):

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            return Response(
                {"message": ("Invalid email or password.")}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@extend_schema(request=None, responses={200: None})
class CustomLogoutView(APIView):
    def post(self, request):
        request.user.token_version += 1
        request.user.save(update_fields=["token_version"])
        if refresh := request.data.get("refresh"):
            try:
                RefreshToken(refresh).blacklist()
            except Exception:
                pass
        return Response({"message": "Logout successful"})


class UserViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["get"], url_path="profile")
    def profile(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @transaction.atomic
    @action(
        detail=False,
        methods=["post"],
        authentication_classes=[],
        permission_classes=[AllowAny],
    )
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
