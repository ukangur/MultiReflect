from PIL import Image
from utils import (
    get_llava_cot_response,
    get_deepseek_vl2_response,
    load_config,
    encode_image,
    get_gpt4v_response,
)

config = load_config()


def get_gpt4v_prompt(image_path, caption):

    return {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Given a caption and image, determine whether the caption matches the image or not, if yes respond <verdict>TRUE</verdict> else <verdict>FALSE</verdict>, also give the consistency score between 0 and 1 like <score>...</score>",
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


def get_llava_cot_prompt(image_path, caption):
    image = Image.open(image_path)
    return {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Given a caption and image, determine whether the caption matches the image or not, if yes respond '<verdict>TRUE</verdict>' else '<verdict>FALSE</verdict>'. Also return a real number confidence score between 0 and 1 in the format '<score>...</score>'.",
                    },
                    {
                        "type": "text",
                        "text": f"Caption: {caption}",
                    },
                    {
                        "type": "image",
                    },
                ],
            }
        ],
        "images": [image],
    }


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
    if config["client"] == "llama":
        prompt = get_llava_cot_prompt(image_path, caption)
        return get_llava_cot_response(prompt, client)
    elif config["client"] == "deepseek":
        prompt = get_deepseek_vl2_prompt(image_path, caption)
        return get_deepseek_vl2_response(prompt, client)
    else:
        prompt = get_gpt4v_prompt(image_path, caption)
        return get_gpt4v_response(prompt, client)
