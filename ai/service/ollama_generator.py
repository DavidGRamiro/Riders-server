import json
from typing import Any

from ollama import ChatResponse, chat
from rest_framework.utils.serializer_helpers import ReturnDict

from ai.constants import SYSTEM_PROMPT, SYSTEM_ROLE, SYSTEM_USER, USER_PROMPT
from ai.serializer import ResponseOllamaSerializer


def generate_response(prompt):
    # We pull the model.  oollama run beam:cloud
    try:
        load_user_prompt = USER_PROMPT.format(
            additional_message=prompt["additional_message"],
            distance=prompt["distance_km"],
        )
        load_system_prompt = SYSTEM_PROMPT.format(
            prefer_curvy_roads=prompt["prefer_curvy_roads"],
            duration_time=prompt["duration_time"],
            route_type=prompt["route_type"],
            origin=prompt["origin"],
            destination=prompt.get("destination"),
        )

        response: ChatResponse = chat(
            model="beam:cloud",
            messages=[
                {"role": SYSTEM_ROLE, "content": load_system_prompt},
                {"role": SYSTEM_USER, "content": load_user_prompt},
            ],
            format="json",
            stream=False,
        )

        # ollama_response_serializer = ResponseOllamaSerializer(
        #     data={
        #         "response": response.message.content,
        #         "role": response.message.role,
        #         "done": response.done,
        #         "total_duration": response.total_duration,
        #     }
        # )
        # ollama_response_serializer.is_valid(raise_exception=True)

        content = response.message.content
        if content is None:
            raise ValueError("Ollama no ha devuelto contenido.")

        content = content.strip()

        if content.startswith("```json"):
            content = content[len("```json") :]

        if content.endswith("```"):
            content = content[:-3]

        main_content = json.loads(content.strip())

        return main_content
    except Exception as e:
        print(e)
