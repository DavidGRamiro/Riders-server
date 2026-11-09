from rest_framework import status
from rest_framework.exceptions import APIException


class OllamaServiceException(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "No se pudo generar la ruta con IA."
    default_code = "ollama_service_error"


class OllamaResponseException(OllamaServiceException):
    default_detail = "La respuesta de Ollama no es válida."
    default_code = "ollama_response_error"


class RoutePersistenceException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "No se pudo guardar la ruta generada."
    default_code = "route_persistence_error"
