import os
import json
from utils import (
    load_config,
    get_gpt4v_response,
    encode_image,
)

config = load_config()


def get_gpt4v_text_to_image_relevance(text_evidence, encoded_image):
    return {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """You'll be provided with an image, along with evidence. Your job is to determine if the evidence is relevant to the determine the factual correctness of the image, and provides useful information to complete the task described in the instruction. If the evidence meets this requirement, respond with [Relevant]; otherwise, generate [Irrelevant]. Also determine the relevancy score of the evidence, on a scale of 0 to 1.
          """,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}",
                            "detail": "high",
                        },
                    },
                    {
                        "type": "text",
                        "text": f"Text Evidence: {text_evidence}",
                    },
                ],
            }
        ]
    }


def get_text_to_image_relevance_sample(file_name, image_path, client):
    responses = {}
    evidence_file = json.load(
        open(f"./data/filtered/{file_name}/text_data/paragraphs.json")
    )
    for key in evidence_file.keys():
        res_list = []
        for evidence in evidence_file[key]:
            try:
                response = ""
                prompt = get_gpt4v_text_to_image_relevance(
                    evidence["text"], image_path
                )
                response = get_gpt4v_response(prompt, client)
                res_list.append(response)
            except:
                res_list.append("Error")
                continue
        responses[key] = res_list
    return responses


def get_gpt4v_image_to_text_relevance(image_evidence_path, caption):
    return {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """You'll be provided with a text, along with an image evidence. Your job is to determine if the evidence is relevant to the determine the factual correctness of the text, and provides useful information to complete the task described in the instruction. If the evidence meets this requirement, respond with [Relevant]; otherwise, generate [Irrelevant]. Also determine the relevancy score of the evidence, on a scale of 0 to 1.
          """,
                    },
                    {
                        "type": "text",
                        "text": f"Text: {caption}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encode_image(image_evidence_path)}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ]
    }



def get_image_to_text_relevance_sample(file_name, caption, client):
    responses = {}
    evidences = os.listdir(f"./data/filtered/{file_name}/image_data/")
    for evidence in evidences:
        try:
            response = ""
            prompt = get_gpt4v_image_to_text_relevance(
                f"./data/filtered/{file_name}/image_data/" + evidence, caption
            )
            response = get_gpt4v_response(prompt, client)

            responses[evidence] = response
        except:
            responses[evidence] = "Error"
            continue
    return responses
