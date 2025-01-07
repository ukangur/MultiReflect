import os
import base64
import json

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_text_to_image_relevance(text_evidence, encoded_image):
    return [
        {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": """You'll be provided with an image, along with evidence. Your job is to determine if the evidence is relevant to the determine the factual correctness of the image, and provides useful information to complete the task described in the instruction. If the evidence meets this requirement, respond with [Relevant]; otherwise, generate [Irrelevant]. Also determine the relevancy score of the evidence, on a scale of 0 to 1.
          """
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
    ]
    
def get_text_to_image_relevance_sample(file_name, encoded_image, client):
    responses = {}
    evidence_file = json.load(open(f'./data/filtered/{file_name}/text_data/paragraphs.json'))
    for key in evidence_file.keys():
        res_list = []
        for evidence in evidence_file[key]:
          try:
            prompt = get_text_to_image_relevance(evidence['text'], encoded_image)
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=prompt,
            )
            res_list.append(response.choices[0].message.content)
          except:
            res_list.append("Error")
            continue
        responses[key] = res_list
    return responses

def get_image_to_text_relevance(image_evidence_path, caption):
    return [
        {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": """You'll be provided with a text, along with an image evidence. Your job is to determine if the evidence is relevant to the determine the factual correctness of the text, and provides useful information to complete the task described in the instruction. If the evidence meets this requirement, respond with [Relevant]; otherwise, generate [Irrelevant]. Also determine the relevancy score of the evidence, on a scale of 0 to 1.
          """
        },
        {
          "type": "text",
          "text": f"Text: {caption}",
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
    ]
    
def get_image_to_text_relevance_sample(file_name, caption, client):
    responses = {}
    evidences = os.listdir(f'./data/filtered/{file_name}/image_data/')
    for evidence in evidences:
      try:
        prompt = get_image_to_text_relevance(f'./data/filtered/{file_name}/image_data/'+evidence, caption)
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=prompt,
            max_tokens=400
        )
        responses[evidence] = response.choices[0].message.content
      except:
        responses[evidence] = "Error"
        continue
    return responses