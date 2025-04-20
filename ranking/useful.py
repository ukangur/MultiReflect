import os
import json
from utils import (
    load_config,
    get_gpt4v_response,
    encode_image,
)

config = load_config()


def get_gpt4v_text_useful(caption, encoded_image, text_evidence):
    return {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
          Given an input text and input image along with an text evidence,
          rate whether the evidence appears to be a helpful and informative answer to determine
          the factuality of the input, from 1 (lowest) - 5 (highest). We call this score perceived
          utility. The detailed criterion is as follows: 5: The evidence provides a complete, highly
          detailed, and informative response to the factuality of the input, fully satisfying the information needs.
          4: The evidence mostly fulfills the need to get the factuality of the input, while there can be some minor improvements
          such as discussing more detailed information, having better structure of the evidence, or 
          improving coherence. 3: The evidence is acceptable, but some major additions or improvements
          are needed to satisfy factuality. 2: The evidence still addresses the main request, but it is
          not complete or not relevant to the input. 1: The response is barely on-topic or completely
          irrelevant.
          """,
                    },
                    {
                        "type": "text",
                        "text": f"Input Text: {caption}\n\nInput Image: ",
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


def get_text_useful_sample(file_name, caption, image_path, client):
    responses = {}
    evidence_file = json.load(
        open(f"./data/filtered/{file_name}/text_data/paragraphs.json")
    )
    for key in evidence_file.keys():
        res_list = []
        for evidence in evidence_file[key]:
            try:
                response = ""
                prompt = get_gpt4v_text_useful(
                    caption, image_path, evidence["text"]
                )
                response = get_gpt4v_response(prompt, client)
                res_list.append(response)
            except:
                res_list.append("Error")
                continue
        responses[key] = res_list
    return responses


def get_gpt4v_image_useful(image_evidence_path, caption, encoded_image):
    return {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
          Given an input text and input image along with an image evidence,
          rate whether the evidence appears to be a helpful and informative answer to determine
          the factuality of the input, from 1 (lowest) - 5 (highest). We call this score perceived
          utility. The detailed criterion is as follows: 5: The evidence provides a complete, highly
          detailed, and informative response to the factuality of the input, fully satisfying the information needs.
          4: The evidence mostly fulfills the need to get the factuality of the input, while there can be some minor improvements
          such as discussing more detailed information, having better structure of the evidence, or 
          improving coherence. 3: The evidence is acceptable, but some major additions or improvements
          are needed to satisfy factuality. 2: The evidence still addresses the main request, but it is
          not complete or not relevant to the input. 1: The response is barely on-topic or completely
          """,
                    },
                    {
                        "type": "text",
                        "text": f"Input Text: {caption}\n\nInput Image: ",
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
                        "text": f"Image Evidence: ",
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

def get_image_useful_sample(file_name, caption, image_path, client):
    responses = {}
    evidences = os.listdir(f"./data/filtered/{file_name}/image_data/")
    for evidence in evidences:
        try:
            prompt = get_gpt4v_image_useful(
                f"./data/filtered/{file_name}/image_data/" + evidence,
                caption,
                image_path,
            )
            responses[evidence] = get_gpt4v_response(prompt, client)
        except:
            responses[evidence] = "Error"
            continue
    return responses
