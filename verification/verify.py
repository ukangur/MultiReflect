import json
import os
from PIL import Image
from utils import (
    load_config,
    get_deepseek_vl2_response,
)

config = load_config()

def deepseekvl2_verification_prompt(
    image_path, caption, text_evidences, image_evidences
):
    text_evidences = ""
    for i in range(len(text_evidences)):
        text_evidences += f"<image> {text_evidences[i]} \n"

    images = []
    images.append(image_path)
    for i in range(len(image_evidences)):
        images.append(image_evidences[i])

    return {
        "messages": [
            {
                "role": "<|User|>",
                "content": """ You will receive an image and caption along with some external documents (evidences).
        Based on the evidences provided you need to determine factual correctness of the input image and caption.
        If the input image and caption are out-of-context output [OUT-OF-CONTEXT], else if factually correct output [TRUE], otherwise [FALSE].
        Also output the confidence score in scale 0 to 1 for the same decision."""
                f"\n \n \t Caption: {caption} \n\nInput Image:"
                "<image>"
                f"n \n \t Evidences : \n{text_evidences}",
                "images": images,
            },
            {"role": "<|Assistant|>", "content": ""},
        ]
    }


def get_response_subs(
    file_name, image_path, caption, text_evidences, image_evidences, client
):
    response = ""
    prompt = deepseekvl2_verification_prompt(
        image_path, caption, text_evidences, image_evidences
    )
    response = get_deepseek_vl2_response(prompt, client)

    if not os.path.exists(f"./data/generated/{file_name}/"):
        os.makedirs(f"./data/generated/{file_name}/")
    with open(f"./data/generated/{file_name}/verification.json", "w") as f:
        json.dump(
            {
                "response": response,
                "num text evidence": len(text_evidences),
                "num image evidence": len(image_evidences),
            },
            f,
        )
