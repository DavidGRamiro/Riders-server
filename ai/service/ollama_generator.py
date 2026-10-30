import json

from ollama import ChatResponse, chat

from ai.constants import SYSTEM_PROMPT, SYSTEM_ROL, USER_ROL, USER_PROMPT
from ai.serializer import ResponseOllamaSerializer


def generate_response(prompt):
    try:
        origin_val = prompt.get("origin") or "No especificado"
        destination_val = prompt.get("destination") or "No especificado"
        route_type_val = prompt.get("route_type") or "No especificado"
        add_msg_val = prompt.get("additional_message") or "Sin preferencias adicionales"

        load_system_prompt = SYSTEM_PROMPT
        load_user_prompt = USER_PROMPT.format(
            origin=origin_val,
            destination=destination_val,
            route_type=route_type_val,
            prefer_curvy_roads="Sí" if prompt.get("prefer_curvy_roads") else "No",
            duration_time=(
                "Sin límite"
                if not prompt.get("duration_time")
                else f"{prompt['duration_time']} horas"
            ),
            distance=(
                "Sin límite" if not prompt.get("distance_km") else f"{prompt['distance_km']} km"
            ),
            additional_message=add_msg_val,
        )

        response: ChatResponse = chat(
            model="beam:cloud",
            messages=[
                {"role": SYSTEM_ROL, "content": load_system_prompt},
                {"role": USER_ROL, "content": load_user_prompt},
            ],
            format="json",
            stream=False,
        )

        content = response.message.content
        assert content is not None, "El contenido de la respuesta no puede ser None"

        data_dict = json.loads(content)
        serializer = ResponseOllamaSerializer(data=data_dict)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
    except Exception as e:
        print(e)
