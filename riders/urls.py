
from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView

from motorcycles.views import MotorcycleViewSet
from routes.views import RouteViewSet
from users.views import UserViewSet

router = routers.DefaultRouter()

router.register(r'user', UserViewSet, basename='users')
router.register(r'motorcycle', MotorcycleViewSet, basename='motorcycle')
router.register(r'route', RouteViewSet, basename='route')

urlpatterns = [
    # Rutas fijas.
    path('admin/', admin.site.urls),
    path('api/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Rutas enlazadas a las apps
    path('api/', include(router.urls)),
]
