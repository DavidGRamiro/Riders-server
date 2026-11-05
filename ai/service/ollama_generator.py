import json
import logging

from django.db import transaction
from geopy import Nominatim
from ollama import ChatResponse, chat

from ai.constants import SYSTEM_PROMPT, SYSTEM_ROL, USER_PROMPT, USER_ROL
from ai.exceptions import (
    OllamaResponseException,
    OllamaServiceException,
    RoutePersistenceException,
)
from users.models import User, UserGeneratedRoute

logger = logging.getLogger(__name__)

OLLAMA_MODEL = "beam:cloud"
REQUIRED_ROUTE_FIELDS = {
    "title",
    "origin",
    "destination",
    "way_points",
    "route_type",
    "prefer_curvy_roads",
    "distance_estimated_km",
}


def generate_route(prompt: dict) -> dict:
    """
    Generate a route from the user's request.

    The returned dict is the domain representation of the route. Serializing it
    for the response is the responsibility of the view.

    :param prompt: validated request data
    :return: route data ready to be serialized
    :raises OllamaServiceException: if the request to Ollama fails
    :raises OllamaResponseException: if Ollama returns an invalid response
    """
    user_prompt = create_user_prompt(prompt)
    raw_response = request_route(user_prompt)
    route_data = parse_route_response(raw_response)
    route_data["coords"] = create_coords(route_data["way_points"])
    return route_data


def generate_and_save_route(prompt: dict, user: User) -> dict:
    """
    Generate a route and persist it for the given user.

    :param prompt: validated request data
    :param user: authenticated user
    :return: route data ready to be serialized
    :raises OllamaServiceException: if the request to Ollama fails
    :raises OllamaResponseException: if Ollama returns an invalid response
    :raises RoutePersistenceException: if the route cannot be saved
    """
    route_data = generate_route(prompt)
    save_generated_route(route_data, user)
    return route_data


def create_user_prompt(prompt: dict) -> str:
    """
    Build the user message sent to Ollama from the validated request data.

    Missing optional values are replaced with sensible defaults so the prompt
    template always receives a complete set of parameters.

    :param prompt: validated request data
    :return: formatted user prompt
    """
    origin_val = prompt.get("origin") or "No especificado"
    destination_val = prompt.get("destination") or "No especificado"
    route_type_val = prompt.get("route_type") or "No especificado"
    add_msg_val = prompt.get("additional_message") or "Sin preferencias adicionales"
    prefer_curvy_roads = "Sí" if prompt.get("prefer_curvy_roads") else "No"
    duration = (
        "Sin límite" if not prompt.get("duration_time") else f"{prompt['duration_time']} horas"
    )
    distance = "Sin límite" if not prompt.get("distance_km") else f"{prompt['distance_km']} km"

    return USER_PROMPT.format(
        origin=origin_val,
        destination=destination_val,
        route_type=route_type_val,
        prefer_curvy_roads=prefer_curvy_roads,
        duration_time=duration,
        distance=distance,
        additional_message=add_msg_val,
    )


def request_route(user_prompt: str) -> str:
    """
    Send the prompt to the Ollama chat model and return its raw content.

    The model is instructed to answer with JSON only, so the returned value is
    expected to be a JSON string ready to be parsed.

    :param user_prompt: user message built by :func:`create_user_prompt`
    :return: raw response content returned by Ollama
    :raises OllamaServiceException: if the request to Ollama fails
    :raises OllamaResponseException: if Ollama returns an empty response
    """
    try:
        response: ChatResponse = chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": SYSTEM_ROL, "content": SYSTEM_PROMPT},
                {"role": USER_ROL, "content": user_prompt},
            ],
            format="json",
            stream=False,
        )
    except Exception as exc:
        logger.exception("Error requesting the route to Ollama")
        raise OllamaServiceException() from exc

    content = response.message.content
    if not content:
        raise OllamaResponseException("La respuesta de Ollama está vacía.")
    return content


def parse_route_response(raw_response: str) -> dict:
    """
    Parse and validate the raw JSON returned by Ollama.

    Checks that the response is valid JSON, is a JSON object, does not contain
    an error, and includes every field listed in ``REQUIRED_ROUTE_FIELDS``.

    :param raw_response: raw content returned by Ollama
    :return: parsed route data
    :raises OllamaResponseException: if the response is invalid or incomplete
    """
    try:
        route_data = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise OllamaResponseException("Ollama no devolvió un JSON válido.") from exc

    if not isinstance(route_data, dict):
        raise OllamaResponseException("La respuesta de Ollama no es un objeto JSON.")

    if error := route_data.get("error"):
        raise OllamaResponseException(f"Ollama devolvió un error: {error}")

    missing_fields = REQUIRED_ROUTE_FIELDS.difference(route_data)
    if missing_fields:
        raise OllamaResponseException(
            "La respuesta de Ollama no contiene los campos requeridos: "
            f"{', '.join(sorted(missing_fields))}."
        )

    return route_data


def create_coords(way_points: list[str]) -> list[dict]:
    """
    Get the complete information for each waypoint using the Nominatim API.

    :param way_points: waypoint names returned by Ollama
    :return: list with the geocoded information of each waypoint; waypoints
        that cannot be geocoded are returned as ``{"position", "msg"}`` entries
    """
    geolocator = Nominatim(user_agent="riders", timeout=10)
    geopy_response = []

    for position in way_points:
        try:
            location = geolocator.geocode(position, language="es")
        except Exception as exc:
            logger.warning("Error geocoding waypoint '%s': %s", position, exc)
            geopy_response.append({"position": position, "msg": "Position not found"})
            continue

        if location is None:
            geopy_response.append({"position": position, "msg": "Position not found"})
            continue

        geopy_response.append({
            "location": location.address,
            "altitude": location.altitude,
            "lat": location.latitude,
            "lon": location.longitude,
            "name": location.raw.get("name"),
        })

    return geopy_response


@transaction.atomic
def save_generated_route(route_data: dict, user: User) -> UserGeneratedRoute:
    """
    Persist the generated route for the given user.

    The ``coords`` and ``way_points`` lists are stored as JSON strings because
    the model fields are plain text.

    :param route_data: route data generated by :func:`generate_route`
    :param user: authenticated user the route belongs to
    :return: created ``UserGeneratedRoute`` instance
    :raises RoutePersistenceException: if the route cannot be saved
    """
    try:
        return UserGeneratedRoute.objects.create(
            id_fk_user=user,
            coords=json.dumps(route_data["coords"]),
            waypoint=json.dumps(route_data["way_points"]),
            distance_km=route_data["distance_estimated_km"],
            route_type=route_data["route_type"],
        )
    except Exception as exc:
        logger.exception("Error saving the generated route for user %s", user.pk)
        raise RoutePersistenceException() from exc
