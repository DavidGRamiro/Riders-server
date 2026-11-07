from rest_framework import status
from rest_framework.exceptions import APIException


class RouteException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid route"
    default_code = "invalid_route"


class RouteGeneratedNoValidError(RouteException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Error guardando la ruta en el servidor."
    default_code = "no_valid_route"
