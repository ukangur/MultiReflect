from PIL import Image
from utils import (
    get_deepseek_vl2_response,
    load_config,
)

config = load_config()

def get_deepseek_vl2_prompt(image_path, caption):
    return {
        "messages": [
            {
                "role": "<|User|>",
                "content": f"<image>\n<|ref|>Given a caption and image, determine whether the caption matches the image or not, if yes respond '<verdict>TRUE</verdict>' else '<verdict>FALSE</verdict>'. Also return a real number confidence score between 0 and 1 in the format '<score>...</score>' Caption : {caption}<|/ref|>.",
                "images": [image_path],
            },
            {"role": "<|Assistant|>", "content": ""},
        ]
    }


def get_response(image_path, caption, client):
    prompt = get_deepseek_vl2_prompt(image_path, caption)
    return get_deepseek_vl2_response(prompt, client)