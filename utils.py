from deepseek_vl2.models import DeepseekVLV2Processor
from deepseek_vl2.utils.io import load_pil_images

from transformers import AutoModelForCausalLM

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
    
class DeepSeekImageTextToTextModel:
    def __init__(self, model_path):
        self.model = (
            AutoModelForCausalLM.from_pretrained(
                model_path,
                trust_remote_code=True,
            )
            .to(torch.bfloat16)
            .cuda()
            .eval()
        )
        self.processor = DeepseekVLV2Processor.from_pretrained(model_path)
        self.tokenizer = self.processor.tokenizer

def get_deepseek_vl2_response(prompt, client):
    messages = prompt["messages"]
    pil_images = load_pil_images(messages)
    prepare_inputs = client.processor(
        conversations=messages, images=pil_images, force_batchify=True, system_prompt=""
    ).to(client.model.device)
    inputs_embeds = client.model.prepare_inputs_embeds(**prepare_inputs)
    outputs = client.model.language.generate(
        inputs_embeds=inputs_embeds,
        attention_mask=prepare_inputs.attention_mask,
        pad_token_id=client.tokenizer.eos_token_id,
        bos_token_id=client.tokenizer.bos_token_id,
        eos_token_id=client.tokenizer.eos_token_id,
        max_new_tokens=512,
        do_sample=False,
        use_cache=True,
    )
    output = client.tokenizer.decode(
        outputs[0].cpu().tolist(), skip_special_tokens=True
    )
    return output