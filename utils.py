import json
import os
import base64

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