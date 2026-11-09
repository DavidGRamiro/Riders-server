from django.contrib import admin
from django.urls import path, include

from rest_framework import routers

from apps.ai.views import OllamaAIViewSet
from apps.auth.views import LoginCustomView, RefreshUserTokenView
from apps.bikes.views import MotorcycleViewSet
from apps.routes.views import RouteViewSet
from apps.users.views import UserViewSet

router = routers.DefaultRouter()

router.register(r"user", UserViewSet, basename="users")
router.register(r"motorcycle", MotorcycleViewSet, basename="motorcycle")
router.register(r"route", RouteViewSet, basename="route")
router.register("ai", OllamaAIViewSet, basename="ollama-ai")

urlpatterns = [
    # Rutas fijas.º
    path("admin/", admin.site.urls),
    path("api/login", LoginCustomView.as_view(), name="login"),
    path("api/refresh", RefreshUserTokenView.as_view(), name="refresh"),
    # Rutas enlazadas a las apps
    path("api/", include(router.urls)),
]
