import json

from geopy import Nominatim
from ollama import ChatResponse, chat

from ai.constants import SYSTEM_PROMPT, SYSTEM_ROL, USER_PROMPT, USER_ROL
from ai.serializer import ResponseOllamaSerializer


def generate_response(prompt):
    """
    Generate response from user request, using Ollama free cloud model.
    After Ollama give us a list of possible waypoints, we call to geopy, and
    they give us complete information about the way points and we return them.
    :param prompt: dict
    :return: ResponseOllamaSerializer serializer object
    """
    origin_val = prompt.get("origin") or "No especificado"
    destination_val = prompt.get("destination") or "No especificado"
    route_type_val = prompt.get("route_type") or "No especificado"
    add_msg_val = prompt.get("additional_message") or "Sin preferencias adicionales"

    load_user_prompt = USER_PROMPT.format(
        origin=origin_val,
        destination=destination_val,
        route_type=route_type_val,
        prefer_curvy_roads="Sí" if prompt.get("prefer_curvy_roads") else "No",
        duration_time=(
            "Sin límite" if not prompt.get("duration_time") else f"{prompt['duration_time']} horas"
        ),
        distance=("Sin límite" if not prompt.get("distance_km") else f"{prompt['distance_km']} km"),
        additional_message=add_msg_val,
    )
    try:
        response: ChatResponse = chat(
            model="beam:cloud",
            messages=[
                {"role": SYSTEM_ROL, "content": SYSTEM_PROMPT},
                {"role": USER_ROL, "content": load_user_prompt},
            ],
            format="json",
            stream=False,
        )

        content = response.message.content
        assert content is not None, "El contenido de la respuesta no es valido"

        data_dict = json.loads(content)
        geo = create_waypoints(data_dict["way_points"])
        data_dict["coords"] = geo

        serializer = ResponseOllamaSerializer(data=data_dict)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
    except Exception as e:
        print(e)


def create_waypoints(waypoints):
    """
    Create waypoints list from ollama waypoints.
    Call to geopy API, and give us complete information about waypoints.
    :param waypoints:
    :return:
    """
    geolocator = Nominatim(user_agent="riders", timeout=10)
    geopy_response = []

    try:
        for position in waypoints:
            location = geolocator.geocode(position, language="es")
            if location:
                geopy_response.append({
                    "location": location.address,
                    "altitude": location.altitude,
                    "lat": location.latitude,
                    "lon": location.longitude,
                    "name": location.raw.get("name", None),
                })
            else:
                geopy_response.append({"position": None, "msg": "Position not found"})
    except Exception as ex:
        geopy_response.append({"detail": "Problem getting geocode positions", "err": str(ex)})
    return geopy_response
