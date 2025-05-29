from utils import (
    load_config,
    get_deepseek_vl2_response,
)

config = load_config()


def get_deepseekvl2_prompt_first(image_path, caption):
    return {
        "messages": [
            {
                "role": "<|User|>",
                "content": """Given a image and caption, please make a judgment on whether finding some external documents
from the web (e.g., Wikipedia) helps to decide whether the image and caption is factually correct. Please answer [Yes] or
[No] and write an explanation. """
                f"<image> Caption: {caption}",
                "images": [image_path],
            },
            {"role": "<|Assistant|>", "content": ""},
        ]
    }


def get_deepseekvl2_prompt_subs(image_path, caption, text_evidences, image_evidences):
    images = []
    images.append(image_path)
    text_evidences_text = ""
    for i in range(len(text_evidences)):
        text_evidences_text += f"<image>\n \t Text Evidence: {text_evidences[i]}\n\n"

    for i in range(len(image_evidences)):
        images.append(image_path)

    messages = [
        {
            "role": "<|User|>",
            "content": f"""<image>\n<|ref|>Given a image and caption along with some external documents (evidences). 
            Your task is to determine whether the factuality of the image and caption can be fully
            verified by the evidence or if it requires further external verification.
            There are three cases:
            - If image and caption can be verified solely with the evidences, then respond with [Continue
            to Use Evidence].
            - If the sentence doesn't require any factual verification (e.g., a subjective sentence or a
            sentence about common sense), then respond with [No Retrieval].
            - If additional information is needed to verify, respond with [Retrieval].
            Please provide explanations for your judgments \n \t Caption : {caption}<|/ref|>."""
            f"{text_evidences_text}",
            "images": images,
        },
        {"role": "<|Assistant|>", "content": ""},
    ]
    return {"messages": messages}


def get_response_first(image_path, caption, client):
    prompt = get_deepseekvl2_prompt_first(image_path, caption)
    return get_deepseek_vl2_response(prompt, client)
    


def get_response_subs(image_path, caption, text_evidences, image_evidences, client):
    prompt = get_deepseekvl2_prompt_subs(
        image_path, caption, text_evidences, image_evidences
    )
    return get_deepseek_vl2_response(prompt, client)
