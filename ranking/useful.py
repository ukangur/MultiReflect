import os
import base64
import json

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_text_useful(caption, encoded_image, text_evidence):
    return [
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
  ]
    
def get_text_useful_sample(file_name, caption, encoded_image, client):
    responses = {}
    evidence_file = json.load(open(f'./data/filtered/{file_name}/text_data/paragraphs.json'))
    for key in evidence_file.keys():
        res_list = []
        for evidence in evidence_file[key]:
          try:
            prompt = get_text_useful(caption, encoded_image, evidence['text'])
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

def get_image_useful(image_evidence_path, caption, encoded_image):
    return [
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
  ]
    
def get_image_useful_sample(file_name, caption, encoded_image, client):
    responses = {}
    evidences = os.listdir(f'./data/filtered/{file_name}/image_data/')
    for evidence in evidences:
      try:
        prompt = get_image_useful(f'./data/filtered/{file_name}/image_data/'+evidence, caption, encoded_image)
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