import json
import os
from PIL import Image
from utils import get_llava_cot_response, load_config, get_deepseek_vl2_response, get_gpt4v_response, encode_image

config = load_config()

def gt4v_verification_prompt(image_path, caption):
    return {"messages":[{
    "role": "user",
    "content": [
        {
        "type": "text",
        "text": """
        You will receive an image and caption.
        Based on the knowledge you have, you need to determine factual correctness of the input image and caption.
        If the input image and caption are out-of-context output [OUT-OF-CONTEXT], else if factually correct output [TRUE], otherwise [FALSE].
        Also output the confidence score in scale 0 to 1 for the same decision.
        """
        },
        {
        "type": "text",
        "text": f"Caption: {caption}",
        },
        {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{encode_image(image_path)}",
            "detail": "high"
            },
        }
    ],
    }]}

def llava_cot_verification_prompt(image_path, caption):
    image = Image.open(image_path)
    return { 
        "messages" : [{
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": """
            You will receive an image and caption.
            Based on the knowledge you have, you need to determine factual correctness of the input image and caption.
            If the input image and caption are out-of-context output [OUT-OF-CONTEXT], else if factually correct output [TRUE], otherwise [FALSE].
            Also output the confidence score in scale 0 to 1 for the same decision.
            """
            },
            {
            "type": "text",
            "text": f"Caption: {caption}",
            },
            {
            "type": "image",
            }
        ],
        }],
        "images" : [image]
    }

def deepseekvl2_verification_prompt(image_path, caption):
    return {"messages":[
    {
        "role": "<|User|>",
        "content": """ You will receive an image and caption.
            Based on the knowledge you have, you need to determine factual correctness of the input image and caption.
            If the input image and caption are out-of-context output [OUT-OF-CONTEXT], else if factually correct output [TRUE], otherwise [FALSE].
            Also output the confidence score in scale 0 to 1 for the same decision."""
            f"\n \n \t Caption: {caption} \n"
            "<image>",
        "images": [image_path],
    },
    {"role": "<|Assistant|>", "content": ""},
]}

def get_response_subs(file_name, image_path, caption, client):
    response = ""
    if config['client']=="llama":
        prompt = llava_cot_verification_prompt(image_path, caption)
        response = get_llava_cot_response(prompt,client)
    elif config['client']=="deepseek":
        prompt = deepseekvl2_verification_prompt(image_path, caption)
        response = get_deepseek_vl2_response(prompt,client)
    else:
        prompt = gt4v_verification_prompt(image_path, caption)
        response = get_gpt4v_response(prompt,client)
    
    if not os.path.exists(f"./data/generated/{file_name}/"):
        os.makedirs(f"./data/generated/{file_name}/")
    with open(f"./data/generated/{file_name}/verification_noevi.json", "w") as f:
        json.dump({"response": response}, f)