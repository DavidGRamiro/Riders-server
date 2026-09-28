from typing import Any

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from motorcycles.serializer import MotorcycleSerializer
from users.models import User
from users.serializer import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


    def get_serializer_class(self):
        if self.action == 'get_user_motorbikes':
            return MotorcycleSerializer
        return super().get_serializer_class()

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

    @action(
        methods=['get'],
        detail=True,
        url_path='motorbikes'
    )
    def get_user_motorbikes(self, request,*args: Any, **kwargs: Any) -> Response:
         user = self.get_object()
         motorcycles = user.motorcycles.all()

         if motorcycles is not None:
             serializer = self.get_serializer(motorcycles, many=True)
             return Response(
                 data=serializer.data,
                 status=status.HTTP_200_OK,
             )
         else:
             return Response(status=status.HTTP_404_NOT_FOUND)
