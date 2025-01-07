import base64
import json
import os

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def verification_prompt(image_path, caption, text_evidences, image_evidences):
    messages =  [{
    "role": "user",
    "content": [
        {
        "type": "text",
        "text": """
        You will receive an image and caption along with some external documents (evidences).
        Based on the evidences provided you need to determine factual correctness of the input image and caption.
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

def get_response_subs(file_name, image_path, caption, text_evidences, image_evidences, client):
    prompt = verification_prompt(image_path, caption, text_evidences, image_evidences)
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=prompt,
    )
    if not os.path.exists(f"./data/generated/{file_name}/"):
        os.makedirs(f"./data/generated/{file_name}/")
    with open(f"./data/generated/{file_name}/verification.json", "w") as f:
        json.dump({"response": response.choices[0].message.content, "num text evidence": len(text_evidences), "num image evidence": len(image_evidences)}, f)