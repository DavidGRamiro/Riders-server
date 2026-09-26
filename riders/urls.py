
from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView

from users.views import UserViewSet

router = routers.DefaultRouter()

router.register(r'user', UserViewSet, basename='users')

urlpatterns = [
    # Rutas fijas.
    path('admin/', admin.site.urls),
    path('api/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Rutas enlazadas a las apps
    path('api/', include(router.urls))
]
