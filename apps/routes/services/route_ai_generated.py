"""Servicio para persistir en base de datos las rutas generadas por la IA.

La ruta generada llega como un diccionario con dos claves:

- ``ollama``: metadatos de la ruta producidos por el modelo (puntos de paso,
  distancia estimada, tipo de ruta, etc.).
- ``route_engine``: resultado del motor de rutas (coordenadas, distancia y
  duración reales).

Este módulo se encarga de mapear esos datos al modelo ``RouteGeneratedByUser``.
"""

from apps.routes.exceptions import RouteGeneratedNoValidError
from apps.routes.models import RouteGeneratedByUser
from apps.users.models import User


def assign_route_to_user(user: User, route_generated: dict):
    """Asocia una ruta generada por la IA a un usuario.

    Extrae la información de ``route_generated`` y crea un registro en
    ``RouteGeneratedByUser``.

    Args:
        user: Usuario al que se le asigna la ruta.
        route_generated: Diccionario con las claves ``ollama`` y
            ``route_engine`` devueltas por el flujo de generación de rutas.

    Returns:
        None.

    Raises:
        RouteGeneratedNoValidError: Si los datos de la ruta son inválidos o
            no se puede crear el registro en base de datos.
    """
    try:
        ollama = route_generated["ollama"]
        route_engine = route_generated["route_engine"]

        RouteGeneratedByUser.objects.create(
            id_fk_user=user,
            coords=route_engine.get("coordinates", {}),
            waypoints=ollama.get("way_points", {}),
            distance_km=ollama.get("distance_estimated_km", 0),
            route_type=ollama.get("route_type", None),
        )
    except Exception as exc:
        raise RouteGeneratedNoValidError from exc
