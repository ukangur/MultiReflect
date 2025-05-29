import json
import os
from PIL import Image
from utils import (
    load_config,
    get_gpt4v_response,
    encode_image,
)

config = load_config()


def gt4v_verification_prompt(image_path, caption):
    return {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
        You will receive an image and caption.
        Based on the knowledge you have, you need to determine factual correctness of the input image and caption.
        If the input image and caption are out-of-context output [OUT-OF-CONTEXT], else if factually correct output [TRUE], otherwise [FALSE].
        Also output the confidence score in scale 0 to 1 for the same decision.
        """,
                    },
                    {
                        "type": "text",
                        "text": f"Caption: {caption}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encode_image(image_path)}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ]
    }


def get_response_subs(file_name, image_path, caption, client):
    prompt = gt4v_verification_prompt(image_path, caption)
    response = get_gpt4v_response(prompt, client)

    if not os.path.exists(f"./data/generated/{file_name}/"):
        os.makedirs(f"./data/generated/{file_name}/")
    with open(f"./data/generated/{file_name}/verification_noevi.json", "w") as f:
        json.dump({"response": response}, f)
