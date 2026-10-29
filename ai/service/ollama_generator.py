from ollama import chat


def generate_response(data):
    # We pull the model.  oollama run beam:cloud
    try:
        response = chat(
            model="beam:cloud",
            messages=[
                {
                    "role": "user",
                    "content": data["message"],
                }
            ],
            format="json",
        )
        return response
    except Exception as e:
        print(e)
