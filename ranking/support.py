import os
import base64
import json

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_text_support(caption, encoded_image, text_evidence):
    return [
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
    
def get_text_support_sample(file_name, caption, encoded_image, client):
    responses = {}
    evidence_file = json.load(open(f'./data/filtered/{file_name}/text_data/paragraphs.json'))
    for key in evidence_file.keys():
        res_list = []
        for evidence in evidence_file[key]:
            try:
              prompt = get_text_support(caption, encoded_image, evidence['text'])
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

def get_image_support(image_evidence_path, caption, encoded_image):
    return [
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
    
def get_image_support_sample(file_name, caption, encoded_image, client):
    responses = {}
    evidences = os.listdir(f'./data/filtered/{file_name}/image_data/')
    for evidence in evidences:
      try:
        prompt = get_image_support(f'./data/filtered/{file_name}/image_data/'+evidence, caption, encoded_image)
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