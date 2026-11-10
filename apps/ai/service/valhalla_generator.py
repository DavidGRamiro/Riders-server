"""
Cliente del motor de routing Valhalla.

Este módulo encapsula toda la comunicación con el servidor de Valhalla: prepara
las coordenadas que devuelve Geopy, construye la petición de routing, decodifica
la geometría de la ruta y la transforma en el objeto que consume el resto de la
aplicación.

El flujo habitual es llamar a:func:`engine_route` con la lista de coordenadas
de los waypoints; internamente se usan:func:`format_coords`,
:func:`call_valhalla_service` y:func:`generate_obj`.

La URL del servidor se lee de la variable de entorno ``VALHALLA_URL``.
"""

import os
from pathlib import Path

import polyline
import requests
from dotenv import load_dotenv

from apps.ai.exceptions import (
    RouteEngineServerNotFoundException,
)

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def engine_route(coords: list):
    """
    Calcula una ruta completa a partir de las coordenadas de sus waypoints.

    Es el punto de entrada del módulo: formatea las coordenadas, solicita la
    ruta a Valhalla y convierte la respuesta en el objeto de dominio de la ruta.

    :param coords: Lista de diccionarios con ``lat`` y ``lon``. Los elementos con
        la clave ``msg`` se consideran no geo codificados y se descartan.
    :return: Diccionario con ``distance`` (km), ``duration`` (segundos) y
        ``coordinates`` (lista de ``{"lat": float, "lon": float}``).
    :raises RouteEngineServerNotFoundException: si falla el formateo, la
        petición a Valhalla o el procesado de la respuesta.
    """
    try:
        locations = format_coords(coords)
        response = call_valhalla_service(locations)
        return generate_obj(response)
    except Exception:
        raise RouteEngineServerNotFoundException


def format_coords(coords: list):
    """
    Adapta las coordenadas de entrada al formato de ``locations`` de Valhalla.

    El primer y el último punto se marcan como ``break`` (parada obligatoria) y
    los intermedios como ``through`` (paso intermedio). Los puntos que no se
    pudieron geo codificar (los que incluyen una clave ``msg``) se omiten.

    :param coords: Lista de diccionarios con ``lat`` y ``lon``.
    :return: Lista de ubicaciones con ``lat``, ``lon`` y ``type``.
    """
    locations = []
    for index, coord in enumerate(coords):
        if coord.get("msg") is not None:
            continue
        locations.append({
            "lat": float(coord["lat"]),
            "lon": float(coord["lon"]),
            "type": "break" if (index == 0 or index == len(coords) - 1) else "through",
        })
    return locations


def call_valhalla_service(locations: list):
    """
    Envía la petición de routing al servidor de Valhalla.

    La petición usa el perfil ``motorcycle``, unidades en kilómetros, respuestas
    en español y la geometría codificada en ``polyline6``, además se ajustan las
    opciones del perfil para evitar autovías (``use_highways`` = 0.0) y
    favorecer los caminos (``use_trails`` = 0.9).

    :param locations: Lista de ubicaciones ya formateadas por
        :func:`format_coords`.
    :return: Respuesta JSON de Valhalla.
    :raises RouteEngineServerNotFoundException: Si la petición falla o el
        servidor devuelve un código de error HTTP.
    """
    url_valhalla = os.environ.get("VALHALLA_URL", "localhost")
    payload = {
        "locations": locations,
        "costing": "motorcycle",
        "units": "kilometers",
        "language": "es-ES",
        "shape_format": "polyline6",
        "costing_options": {"motorcycle": {"use_highways": 0.0, "use_trails": 0.9}},
    }
    try:
        response = requests.post(url_valhalla, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception:
        raise RouteEngineServerNotFoundException


def generate_obj(response):
    """
    Transforma la respuesta de Valhalla en el objeto de ruta de la aplicación.

    Recorre todas las etapas (``legs``) del viaje, decodifica cada geometría
    ``polyline6`` y concatena sus puntos en una única lista de coordenadas.

    :param response: Respuesta JSON devuelta por Valhalla.
    :return: Diccionario con ``distance`` (km), ``duration`` (segundos) y
        ``coordinates`` (lista de ``{"lat": float, "lon": float}``).
    """
    trip = response["trip"]
    coordinates = []

    for leg in trip["legs"]:
        points = polyline.decode(leg["shape"], precision=6)

        for lat, lon in points:
            coordinates.append({
                "lat": float(lat),
                "lon": float(lon),
            })

    return {
        "distance": trip["summary"]["length"],
        "duration": trip["summary"]["time"],
        "coordinates": coordinates,
    }
