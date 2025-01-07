import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def get_prompt(image_path, caption):
    return [{
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Given a caption and image, determine whether the caption matches the image or not, if yes respond <verdict>TRUE</verdict> else <verdict>FALSE</verdict>, also give the consistency score between 0 and 1 like <score>...</score>"
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
    
def get_response(image_path, caption, client):
    prompt = get_prompt(image_path, caption)
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=prompt,
    )
    return response.choices[0].message.content