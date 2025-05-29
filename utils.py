
from transformers import AutoModelForCausalLM
from openai import OpenAI
from auto_round import AutoRoundConfig
import torch
import json
import os
import base64
import re
import yaml


def load_config(config_file="config.yaml"):
    """Load configuration settings from a YAML file."""
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config

config = load_config
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
        return base64.b64encode(image_file.read()).decode("utf-8")

class GptImagetextToTextModel:
    def __init__(self, api_key):
        return OpenAI(api_key=api_key, timeout=100)
    
def get_gpt4v_response(prompt, client):
    messages = prompt["messages"]
    response = client.chat.completions.create(
        model= config["model_id"],
        messages=messages,
    )
    return response.choices[0].message.content
