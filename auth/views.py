from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from auth.serializer import UserLoginSerializer, RefreshUserTokenSerializer


class LoginCustomView(TokenObtainPairView):
    serializer_class = UserLoginSerializer


class RefreshUserTokenView(TokenRefreshView):
    serializer_class = RefreshUserTokenSerializer
