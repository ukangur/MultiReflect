from utils import (
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


def get_response(image_path, caption, client):
    prompt = get_gpt4v_prompt(image_path, caption)
    return get_gpt4v_response(prompt, client)
