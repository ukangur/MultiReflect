import os
import json
from PIL import Image
from utils import get_llava_cot_response

def get_text_support(caption, image_path, text_evidence):
    image = Image.open(image_path)
    return {
      "messages" : [
          {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": """
            You will receive an input text, input image and text evidence towards determining the factuality of the input.
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
            Output Entailment like [Fully supported], [Partially supported] or [No support / Contradictory]
            """
          },
          {
            "type": "text",
            "text": f"Input Text: {caption}\n\nInput Image: ",
          },
          {
            "type": "image",
          },
          {
            "type": "text",
            "text": f"Text Evidence: {text_evidence}",
          },
        ],
      },
    ],
    "images" : [image]
    }
    
def get_text_support_sample(file_name, caption, image_path, client):
    responses = {}
    evidence_file = json.load(open(f'./data/filtered/{file_name}/text_data/paragraphs.json'))
    for key in evidence_file.keys():
        res_list = []
        for evidence in evidence_file[key]:
            try:
              prompt = get_text_support(caption, image_path, evidence['text'])
              response = get_llava_cot_response(prompt, client)
              res_list.append(response)
            except:
              res_list.append("Error")
              continue
        responses[key] = res_list
    return responses

def get_image_support(image_evidence_path, caption, image_path):
    
    image = Image.open(image_path)
    ev_image = Image.open(image_evidence_path)
    images = [image, ev_image]
    return {
      "messages" : [
          {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": """
            You will receive an input text, input image and image evidence towards determining the factuality of the input.
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
            
            Output Entailment on the first line and the explanation on the second line.
            """
          },
          {
            "type": "text",
            "text": f"Input Text: {caption}\n\nInput Image: ",
          },
          {
            "type": "image",
          },
          {
            "type": "text",
            "text": f"Image Evidence: ",
          },
          {
            "type": "image",
          },
        ],
      }
    ],
    "images" : images
    }
    
def get_image_support_sample(file_name, caption, image_path, client):
    responses = {}
    evidences = os.listdir(f'./data/filtered/{file_name}/image_data/')
    for evidence in evidences:
      try:
        prompt = get_image_support(f'./data/filtered/{file_name}/image_data/'+evidence, caption, image_path)
        response = get_llava_cot_response(prompt, client)
        responses[evidence] = response
      except:
        responses[evidence] = "Error"
        continue
    return responses