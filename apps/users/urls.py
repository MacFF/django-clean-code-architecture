from django.urls import include, path
from rest_framework import routers

from apps.users.views import UserViewSet


router = routers.DefaultRouter()
router.register(r"user", UserViewSet, basename="user-auth")

api_v1_urls = (router.urls, "v1")


urlpatterns = [
    path("v1/", include(api_v1_urls)),
]
