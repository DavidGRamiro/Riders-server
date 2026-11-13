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
        prompt = route_generated["prompt"]
        code = generate_unique_code()

        RouteGeneratedByUser.objects.create(
            id_fk_user=user,
            coords=route_engine.get("coordinates", {}),
            waypoints=ollama.get("way_points", {}),
            distance_km=route_engine.get("distance", 0),
            route_type=ollama.get("route_type", None),
            title=ollama.get("title") or "Title of route",
            prompt=prompt.get("additional_message"),
            route_code=code,
            way_points_coords=ollama.get("way_points_coords", {}),
            duration=route_engine.get("duration", 0),
        )
    except Exception as exc:
        raise RouteGeneratedNoValidError from exc


def generate_unique_code() -> str:
    last_route: RouteGeneratedByUser | None = (
        RouteGeneratedByUser.objects
        .exclude(route_code__isnull=True)
        .exclude(route_code="")
        .order_by("-id")
        .first()
    )
    if not last_route:
        return "RI/0"

    last_code = last_route.route_code.split("/")[-1]
    try:
        number = int(last_code)
    except TypeError, ValueError:
        number = -1
    return f"RI/{number + 1}"
