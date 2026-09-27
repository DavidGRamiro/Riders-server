from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.serializer import UserSerializer


# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request,*args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = self.get_object()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)