import os
import json
from PIL import Image
from utils import (
    load_config,
    encode_image,
    get_deepseek_vl2_response,
)

config = load_config()

def get_deepseekvl2_text_support(caption, image_path, text_evidence):
    return {
        "messages": [
            {
                "role": "<|User|>",
                "content": """You will receive an input text, input image and text evidence towards determining the factuality of the input.
            Your task is to evaluate if the input is fully supported by the information provided
            in the evidence.
            Use the following entailment scale to generate a score:
            - [Fully supported] - All information in input is supported by the evidence, or extractions
            from the evidence.
            - [Partially supported] - The input is supported by the evidence to some extent, but there
            is major information in the input that is not discussed in the evidence. For example, if
            the input asks about two concepts and the evidence only discusses either of them, it should
            be considered a [Partially supported].
            - [No support / Contradictory] - The input completely ignores evidence, is unrelated to the
            evidence, or contradicts the evidence. This can also happen if the evidence is irrelevant to the
            instruction.
            Make sure to not use any external information/knowledge to judge whether the input is true or not.
            Only check whether the input is supported by the evidence, and not whether the input follows the instructions or not.
            Output Entailment like [Fully supported], [Partially supported] or [No support / Contradictory]"""
                f"\n \n \t Input Text: {caption} \n\nInput Image:"
                "<image>"
                f"\n \n \t \t Text Evidence {text_evidence}",
                "images": [image_path],
            },
            {"role": "<|Assistant|>", "content": ""},
        ]
    }


def get_text_support_sample(file_name, caption, image_path, client):
    responses = {}
    evidence_file = json.load(
        open(f"./data/filtered/{file_name}/text_data/paragraphs.json")
    )
    for key in evidence_file.keys():
        res_list = []
        for evidence in evidence_file[key]:
            try:
                response = ""
                prompt = get_deepseekvl2_text_support(
                    caption, image_path, evidence["text"]
                )
                response = get_deepseek_vl2_response(prompt, client)
                res_list.append(response)
            except:
                res_list.append("Error text")
                continue
        responses[key] = res_list
    return responses

def get_deepseekvl2_image_support(image_evidence_path, caption, image_path):

    images = [image_path, image_evidence_path]
    return {
        "messages": [
            {
                "role": "<|User|>",
                "content": """You will receive an input text, input image and image evidence towards determining the factuality of the input.
            Your task is to evaluate if the input is fully supported by the information provided
            in the evidence.
            Use the following entailment scale to generate a score:
            - [Fully supported] - All information in input is supported by the evidence, or extractions
            from the evidence.
            - [Partially supported] - The input is supported by the evidence to some extent, but there
            is major information in the input that is not discussed in the evidence. For example, if
            the input asks about two concepts and the evidence only discusses either of them, it should
            be considered a [Partially supported].
            - [No support / Contradictory] - The input completely ignores evidence, is unrelated to the
            evidence, or contradicts the evidence. This can also happen if the evidence is irrelevant to the
            instruction.
            Make sure to not use any external information/knowledge to judge whether the input is true or not.
            Only check whether the input is supported by the evidence, and not whether the input follows the instructions or not.
            
            Output Entailment like [Fully supported], [Partially supported] or [No support / Contradictory]"""
                f"\n \n \t Input Text: {caption} \n\nInput Image:"
                "<image>"
                "\n \n \t \t Image Evidence: "
                "<image>",
                "images": images,
            },
            {"role": "<|Assistant|>", "content": ""},
        ]
    }


def get_image_support_sample(file_name, caption, image_path, client):
    responses = {}
    evidences = os.listdir(f"./data/filtered/{file_name}/image_data/")
    for evidence in evidences:
        try:
            response = ""
            prompt = get_deepseekvl2_image_support(
                f"./data/filtered/{file_name}/image_data/" + evidence,
                caption,
                image_path,
            )
            response = get_deepseek_vl2_response(prompt, client)
            responses[evidence] = response
        except:
            responses[evidence] = "Error image"
            continue
    return responses
