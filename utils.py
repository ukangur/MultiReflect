from transformers import MllamaForConditionalGeneration, AutoProcessor
from auto_round import AutoRoundConfig
import json
import os
import base64
import re

class ImageTextToImageModel():
    def __init__(self, checkpoint):
        self.model =  MllamaForConditionalGeneration.from_pretrained(
                checkpoint,
                torch_dtype="auto",
                device_map="auto"
            )
        self.processor = AutoProcessor.from_pretrained(checkpoint)
        
def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as file:
        return json.load(file)
    
def save_json(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
        
def append_jsonl(data, file_path):
    with open(file_path, "a") as file:
        file.write(json.dumps(data) + "\n")
        
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_llava_cot_response(prompt,client):
    """Function that returns Llava_COT responses given a prompt and client object"""
    messages = prompt["messages"]
    images = prompt["images"]
    input_text = client.processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = client.processor(
      images,
      input_text,
      add_special_tokens=False,
      return_tensors="pt"
    ).to(client.model.device)
    output = client.model.generate(**inputs, max_new_tokens=2048)
    output = client.processor.decode(output[0])
    conclusion = re.search(r'<CONCLUSION>(.*?)</CONCLUSION>',output,re.DOTALL).group(1)
    return conclusion