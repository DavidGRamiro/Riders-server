
from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from users.views import UserViewSet

router = routers.DefaultRouter()

router.register(r'user', UserViewSet, basename='users')

urlpatterns = [
    # Rutas fijas.
    path('admin/', admin.site.urls),
    # Rutas enlazadas a las apps
    path('api/', include(router.urls))
]
