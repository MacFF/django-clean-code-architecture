from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views import CustomLoginView, CustomLogoutView

api_patterns = [
    # auth
    path("v1/login/", CustomLoginView.as_view(), name="auth_login"),
    path("v1/logout/", CustomLogoutView.as_view(), name="auth_logout"),
    path("v1/refresh-token/", TokenRefreshView.as_view(), name="token_refresh"),
    # api
    path("", include("apps.users.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_patterns)),
    # Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
