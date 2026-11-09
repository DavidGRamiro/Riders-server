import json
import logging

from ollama import ChatResponse, chat

from apps.ai.constants import SYSTEM_PROMPT, SYSTEM_ROL, USER_PROMPT, USER_ROL
from apps.ai.exceptions import (
    OllamaResponseException,
    OllamaServiceException,
)

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
    route_data = validate_response(raw_response)
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


def validate_response(raw_response: str) -> dict:
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
