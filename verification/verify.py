import json
import os
from PIL import Image
from utils import get_llava_cot_response


def verification_prompt(image_path, caption, text_evidences, image_evidences):
    images = []
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """
        You will receive an image and caption along with some external documents (evidences).
        Based on the evidences provided you need to determine factual correctness of the input image and caption.
        If the input image and caption are out-of-context output [OUT-OF-CONTEXT], else if factually correct output [TRUE], otherwise [FALSE].
        Also output the confidence score in scale 0 to 1 for the same decision.
        """,
                },
                {
                    "type": "text",
                    "text": f"Caption: {caption}",
                },
                {
                    "type": "image",
                },
                {
                    "type": "text",
                    "text": f"Evidences:",
                },
            ],
        }
    ]
    image = Image.open(image_path)
    images.append(image)
    for i in range(len(text_evidences)):
        messages[0]["content"].append(
            {"type": "text", "text": f"Text Evidence: {text_evidences[i]}"}
        )
    messages[0]["content"].append({"type": "text", "text": f"Image Evidences:"})
    for i in range(len(image_evidences)):
        messages[0]["content"].append(
            {
                "type": "image",
            }
        )
        image = Image.open(image_evidences[i])
        images.append(image)
    return {"messages": messages, "images": images}


def get_response_subs(
    file_name, image_path, caption, text_evidences, image_evidences, client
):
    prompt = verification_prompt(image_path, caption, text_evidences, image_evidences)
    response = get_llava_cot_response(prompt, client)
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
