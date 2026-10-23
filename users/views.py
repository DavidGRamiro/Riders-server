from xml.dom import ValidationErr

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from users.exceptions import UserException
from users.models import User
from users.serializer import UserLoginSerializer, UserSerializer
from users.services import create_user_authenticate


class LoginCustomView(TokenObtainPairView):
    serializer_class = UserLoginSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        try:
            response = create_user_authenticate(request.data)
            return Response(response, status=status.HTTP_201_CREATED)
        except UserException as e:
            return Response(data=e.get_full_details(), status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        user = self.get_object()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=True, url_path="logout", url_name="logout")
    def logout(self, request, pk=None):
        try:
            user = self.get_object()
            user.is_online = False
            user.save(update_fields=["is_online"])
            return Response(data={"Usuario offline"}, status=status.HTTP_204_NO_CONTENT)
        except UserException:
            return Response(status=status.HTTP_404_NOT_FOUND)
