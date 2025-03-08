from transformers import MllamaForConditionalGeneration, AutoProcessor
from deepseek_vl2.models import DeepseekVLV2Processor
from deepseek_vl2.utils.io import load_pil_images

from transformers import AutoModelForCausalLM

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


class LlamaImageTextToTextModel:
    def __init__(self, checkpoint):
        self.model = MllamaForConditionalGeneration.from_pretrained(
            checkpoint, torch_dtype="auto", device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained(checkpoint)


def DeepSeekImageTextToTextModel():
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


def get_llava_cot_response(prompt, client):
    """Function that returns Llava_COT responses given a prompt and client object"""
    messages = prompt["messages"]
    images = prompt["images"]
    input_text = client.processor.apply_chat_template(
        messages, add_generation_prompt=True
    )
    inputs = client.processor(
        images, input_text, add_special_tokens=False, return_tensors="pt"
    ).to(client.model.device)
    output = client.model.generate(**inputs, max_new_tokens=2048)
    output = client.processor.decode(output[0])
    conclusion = re.search(r"<CONCLUSION>(.*?)</CONCLUSION>", output, re.DOTALL).group(
        1
    )
    return conclusion


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


def get_gpt4v_response(prompt, client):
    messages = prompt["messages"]
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=messages,
    )
    return response.choices[0].message.content
