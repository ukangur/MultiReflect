import os
import json
from PIL import Image
from utils import get_llava_cot_response, load_config, get_gpt4v_response, encode_image, get_deepseek_vl2_response

config = load_config()

def get_gpt4v_text_useful(caption, encoded_image, text_evidence):
    return {"messages" :[
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
          """
        },
        {
          "type": "text",
          "text": f"Input Text: {caption}\n\nInput Image: ",
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{encoded_image}",
            "detail": "high"
          },
        },
        {
          "type": "text",
          "text": f"Text Evidence: {text_evidence}",
        },
      ],
    }
  ]}
def get_llava_cot_text_useful(caption, image_path, text_evidence):
    image = Image.open(image_path)
    return {
      "messages" : [
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
      }
    ],
    "images" : [image]
    }
def get_deepseekvl2_text_useful(caption, image_path, text_evidence):
    image = Image.open(image_path)
    return { "messages":[
        {
            "role": "<|User|>",
            "content": """Given an input text and input image along with an text evidence,
                rate whether the evidence appears to be a helpful and informative answer to determine
                the factuality of the input, from 1 (lowest) - 5 (highest). We call this score perceived
                utility. The detailed criterion is as follows: 5: The evidence provides a complete, highly
                detailed, and informative response to the factuality of the input, fully satisfying the information needs.
                4: The evidence mostly fulfills the need to get the factuality of the input, while there can be some minor improvements
                such as discussing more detailed information, having better structure of the evidence, or 
                improving coherence. 3: The evidence is acceptable, but some major additions or improvements
                are needed to satisfy factuality. 2: The evidence still addresses the main request, but it is
                not complete or not relevant to the input. 1: The response is barely on-topic or completely
                irrelevant. """
                "\n\t Input Image and Input Text \n"
                f"<image> is the Input Image and Input Text is {caption}"
                "\n\t Text Evidence \n"
                f"{text_evidence}",
            "images": [image_path],
        },
        {"role": "<|Assistant|>", "content": ""},
    ]}
    
def get_text_useful_sample(file_name, caption, image_path, client):
    responses = {}
    evidence_file = json.load(open(f'./data/filtered/{file_name}/text_data/paragraphs.json'))
    for key in evidence_file.keys():
        res_list = []
        for evidence in evidence_file[key]:
          try:
            response = ""
            if config['client']=="llama":
                prompt = get_llava_cot_text_useful(caption, image_path, evidence['text'])
                response = get_llava_cot_response(prompt, client)
            elif config['client']=="deepseek":
                prompt = get_deepseekvl2_text_useful(caption, image_path, evidence['text'])
                response = get_deepseek_vl2_response(prompt, client)
            else:
                prompt = get_llava_cot_text_useful(caption, image_path, evidence['text'])
                response = get_gpt4v_response(prompt, client)
            res_list.append(response)
          except:
            res_list.append("Error")
            continue
        responses[key] = res_list
    return responses

def get_gpt4v_image_useful(image_evidence_path, caption, encoded_image):
    return {"messages" : [
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
          """
        },
        {
          "type": "text",
          "text": f"Input Text: {caption}\n\nInput Image: ",
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{encoded_image}",
            "detail": "high"
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
            "detail": "high"
          },
        },
      ],
    }
  ]}

def get_llava_cot_image_useful(image_evidence_path, caption, image_path):
    image = Image.open(image_path)
    image_ev = Image.open(image_evidence_path)
    images = [image, image_ev]
    return {
      "messages" : [
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

def get_deepseekvl2_image_useful(image_evidence_path, caption, image_path):
    images = [image_path, image_evidence_path]
    return {"messages":[
        {
            "role": "<|User|>",
            "content": """Given an input text and input image along with an image evidence,
                rate whether the evidence appears to be a helpful and informative answer to determine
                the factuality of the input, from 1 (lowest) - 5 (highest). We call this score perceived
                utility. The detailed criterion is as follows: 5: The evidence provides a complete, highly
                detailed, and informative response to the factuality of the input, fully satisfying the information needs.
                4: The evidence mostly fulfills the need to get the factuality of the input, while there can be some minor improvements
                such as discussing more detailed information, having better structure of the evidence, or 
                improving coherence. 3: The evidence is acceptable, but some major additions or improvements
                are needed to satisfy factuality. 2: The evidence still addresses the main request, but it is
                not complete or not relevant to the input. 1: The response is barely on-topic or completely """
                "\n\t Input Image and Input Text \n"
                f"<image> is the Input Image and Input Text is {caption} \n"
                "\n\t Image Evidence \n"
                f"<image> is the Image Evidence",
            "images": images,
        },
        {"role": "<|Assistant|>", "content": ""},
    ]}

def get_image_useful_sample(file_name, caption, image_path, client):
    responses = {}
    evidences = os.listdir(f'./data/filtered/{file_name}/image_data/')
    for evidence in evidences:
      try:
        if config['client']=="llama":
            prompt = get_llava_cot_image_useful(f'./data/filtered/{file_name}/image_data/'+evidence, caption, image_path)
            responses[evidence] = get_llava_cot_response(prompt, client)
        elif config['client']=="deepseek":
           prompt = get_deepseekvl2_image_useful(f'./data/filtered/{file_name}/image_data/'+evidence, caption, image_path)
           responses[evidence] = get_deepseek_vl2_response(prompt, client)
        else:
            prompt = get_gpt4v_image_useful(f'./data/filtered/{file_name}/image_data/'+evidence, caption, image_path)
            responses[evidence] = get_gpt4v_response(prompt, client)
      except:
        responses[evidence] = "Error"
        continue
    return responses