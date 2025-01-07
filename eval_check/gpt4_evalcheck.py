import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def get_prompt_first(image_path, caption):
    return [{
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
    }]

def get_prompt_subs(image_path, caption, text_evidences, image_evidences):
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
    return messages
    
def get_response_first(image_path, caption, client):
    prompt = get_prompt_first(image_path, caption)
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=prompt,
    )
    return response.choices[0].message.content

def get_response_subs(image_path, caption, text_evidences, image_evidences, client):
    prompt = get_prompt_subs(image_path, caption, text_evidences, image_evidences)
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=prompt,
    )
    return response.choices[0].message.content