from PIL import Image
from utils import get_llava_cot_response

def get_prompt(image_path, caption):
    image = Image.open(image_path)
    return {"messages":[{
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Given a caption and image, determine whether the caption matches the image or not, if yes respond '<verdict>TRUE</verdict>' else '<verdict>FALSE</verdict>'. Also return a real number confidence score between 0 and 1 in the format '<score>...</score>'."
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
    "images": [image]}
    
def get_response(image_path, caption, client):
    prompt = get_prompt(image_path, caption)
    return get_llava_cot_response(prompt,client)