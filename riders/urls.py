from django.contrib import admin
from django.urls import path, include

from rest_framework import routers

from ai.views import OllamaAI
from bikes.views import MotorcycleViewSet
from routes.views import RouteViewSet
from users.views import UserViewSet, LoginCustomView

router = routers.DefaultRouter()

router.register(r"user", UserViewSet, basename="users")
router.register(r"motorcycle", MotorcycleViewSet, basename="motorcycle")
router.register(r"route", RouteViewSet, basename="route")

urlpatterns = [
    # Rutas fijas.º
    path("admin/", admin.site.urls),
    path("api/login", LoginCustomView.as_view(), name="login"),
    # Rutas enlazadas a las apps
    path("api/", include(router.urls)),
    # Ruta especifica para la IA
    path("api/ia", OllamaAI.as_view(), name="ia"),
]
