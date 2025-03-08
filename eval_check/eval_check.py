from PIL import Image
from utils import get_llava_cot_response, encode_image, load_config, get_gpt4v_response, get_deepseek_vl2_response

config=load_config()

def get_gpt4v_prompt_first(image_path, caption):
    return {"messages":[{
    "role": "user",
    "content": [
        {
        "type": "text",
        "text": """Given a image and caption, please make a judgment on whether finding some external documents
from the web (e.g., Wikipedia) helps to decide whether the image and caption is factually correct. Please answer [Yes] or
[No] and write an explanation."""
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
        },
    ],
    }]}

def get_gpt4v_prompt_subs(image_path, caption, text_evidences, image_evidences):
    messages =  [{
    "role": "user",
    "content": [
        {
        "type": "text",
        "text": """Given a image and caption along with some external documents (evidences). 
        Your task is to determine whether the factuality of the image and caption can be fully
        verified by the evidence or if it requires further external verification.
        There are three cases:
        - If image and caption can be verified solely with the evidences, then respond with [Continue
        to Use Evidence].
        - If the sentence doesn't require any factual verification (e.g., a subjective sentence or a
        sentence about common sense), then respond with [No Retrieval].
        - If additional information is needed to verify, respond with [Retrieval].
        Please provide explanations for your judgments"""
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
        },
        {
        "type": "text",
        "text": f"Evidences:",
        },
    ],
    }]
    for i in range(len(text_evidences)):
        messages[0]["content"].append({
            "type": "text",
            "text": f"Text Evidence: {text_evidences[i]}"
        })
    messages[0]["content"].append({
        "type": "text",
        "text": f"Image Evidences:"
    })
    for i in range(len(image_evidences)):
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image(image_evidences[i])}",
                "detail": "high"
            }
        })
    return {"messages": messages}

def get_llava_cot_prompt_first(image_path, caption):
    image = Image.open(image_path)
    return {
        "messages": [{
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": """
            Given a image and caption, please make a judgment on whether finding some external documents
            from the web (e.g., Wikipedia) helps to decide whether the image and caption is factually correct. Please answer [Yes] or
            [No] and write an explanation.
            """
            },
            {
            "type": "text",
            "text": f"Caption: {caption}",
            },
            {
            "type": "image",
            },
        ],
        }],
        "images": [image]
    }

def get_llava_cot_prompt_subs(image_path, caption, text_evidences, image_evidences):
    images = []
    image = Image.open(image_path)
    images.append(image)
    messages =  [{
    "role": "user",
    "content": [
        {
        "type": "text",
        "text": """Given a image and caption along with some external documents (evidences). 
        Your task is to determine whether the factuality of the image and caption can be fully
        verified by the evidence or if it requires further external verification.
        There are three cases:
        - If image and caption can be verified solely with the evidences, then respond with [Continue
        to Use Evidence].
        - If the sentence doesn't require any factual verification (e.g., a subjective sentence or a
        sentence about common sense), then respond with [No Retrieval].
        - If additional information is needed to verify, respond with [Retrieval].
        Please provide explanations for your judgments"""
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
    }]
    for i in range(len(text_evidences)):
        messages[0]["content"].append({
            "type": "text",
            "text": f"Text Evidence: {text_evidences[i]}"
        })
    messages[0]["content"].append({
        "type": "text",
        "text": f"Image Evidences:"
    })
    for i in range(len(image_evidences)): 
        messages[0]["content"].append({
            "type": "image",
        })
        image = Image.open(image_evidences[i])
        images.append(image)
    return {
        "messages" : messages,
        "images" : images
    }

def get_deepseekvl2_prompt_first(image_path, caption):
    return {"messages":[
    {
        "role": "<|User|>",
        "content": """Given a image and caption, please make a judgment on whether finding some external documents
from the web (e.g., Wikipedia) helps to decide whether the image and caption is factually correct. Please answer [Yes] or
[No] and write an explanation. """
f"<image> Caption: {caption}",
        "images": [image_path],
    },
    {"role": "<|Assistant|>", "content": ""},
]}

def get_deepseekvl2_prompt_subs(image_path, caption, text_evidences, image_evidences):
    images = []
    images.append(image_path)
    text_evidences_text = ""
    for i in range(len(text_evidences)):
        text_evidences_text += f"<image>\n \t Text Evidence: {text_evidences[i]}\n\n"
       
    for i in range(len(image_evidences)):
        images.append(image_path)
       
    messages =  [
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
    
    return {"messages" : messages}

def get_response_first(image_path, caption, client):
    if config['client']=="llama":
        prompt = get_llava_cot_prompt_first(image_path, caption)
        return get_llava_cot_response(prompt,client)
    elif config['client']=="deepseek":
        prompt = get_deepseekvl2_prompt_first(image_path, caption)
        return get_deepseek_vl2_response(prompt, client)
    else:
        prompt = get_gpt4v_prompt_first(image_path, caption)
        return get_gpt4v_response(prompt, client)
    
def get_response_subs(image_path, caption, text_evidences, image_evidences, client):
    if config['client']=="llama":
        prompt = get_llava_cot_prompt_subs(image_path, caption, text_evidences, image_evidences)
        return get_llava_cot_response(prompt,client)
    elif config['client']=="deepseek":
        prompt = get_deepseekvl2_prompt_subs(image_path, caption, text_evidences, image_evidences)
        return get_deepseek_vl2_response(prompt,client)
    else:
        prompt = get_gpt4v_prompt_subs(image_path, caption, text_evidences, image_evidences)
        return get_gpt4v_response(prompt, client)
    

