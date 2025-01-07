import spacy
import requests
import json
from google.cloud import vision
from bs4 import BeautifulSoup

nlp = spacy.load('en_core_web_sm')
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36 Edg/122.0.0.0', 'Referer': 'https://www.google.com/'}
client = vision.ImageAnnotatorClient()

def get_entities(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))
    return entities

def create_query(entities, sep=" "):
    query = ""
    for ent in entities:
        query += ent[0] + sep
    return query

def get_wikipedia_data(query):
    try:
        url = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=" + query + "&format=json"
        response = requests.get(url, timeout=60)
        data = json.loads(response.text)
        return data
    except Exception as e:
        return {}
    
def get_google_data(query):
    try:
        url = "https://www.googleapis.com/customsearch/v1?key=AIzaSyCXi8wXOFREwIwDZ0B4OqD5L2EKSmyoo_M&cx=b7f8c7d4cce094056&q=" + query
        response = requests.get(url, timeout=60)
        data = response.json()
        return data            
    except Exception as e:
        return {}
    
def get_bing_search_results(query):
    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {
        "Content-Type": "multipart/form-data",
        "Ocp-Apim-Subscription-Key": "929c5b48185c49238f06ef8ce0bfe4a9",
    }
    params = {
        "q": query,
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=60)
        data = response.json()
        return data
    except Exception as e:
        return {}
    
def get_inverse_image_response(content):
    data = {}
    try:
        image = vision.Image(content=content)
        response = client.web_detection(image=image)
        annotations = response.web_detection
        if annotations.best_guess_labels:
            data['best_guess_labels'] = []
            for label in annotations.best_guess_labels:
                data['best_guess_labels'].append(label.label)
        if annotations.pages_with_matching_images:
            data['pages_with_matching_images'] = []
            for page in annotations.pages_with_matching_images:
                if page.full_matching_images:
                    for image in page.full_matching_images:
                        data['pages_with_matching_images'].append({"url": page.url, "title": page.page_title, "image": image.url, "matching": "full"})
                if page.partial_matching_images:
                    for image in page.partial_matching_images:
                        data['pages_with_matching_images'].append({"url": page.url, "title": page.page_title, "image": image.url, "matching": "partial"})
        if annotations.full_matching_images:
            data['full_matching_images'] = []
            for image in annotations.full_matching_images:
                data['full_matching_images'].append(image.url)
        if annotations.partial_matching_images:
            data['partial_matching_images'] = []
            for image in annotations.partial_matching_images:
                data['partial_matching_images'].append(image.url)
        if annotations.web_entities:
            data['web_entities'] = []
            for entity in annotations.web_entities:
                data['web_entities'].append({"description": entity.description, "score": entity.score, "id": entity.entity_id})
        if annotations.visually_similar_images:
            data['visually_similar_images'] = []
            for image in annotations.visually_similar_images:
                data['visually_similar_images'].append(image.url)
        return data
    except Exception as e:
        return data

def get_bing_image_response(content):
    base_url = "https://api.bing.microsoft.com/v7.0/images/visualsearch"
    bing_inverse_headers = {
        "Content-Type": "multipart/form-data",
        "Ocp-Apim-Subscription-Key": "929c5b48185c49238f06ef8ce0bfe4a9",
    }
    data = {}
    try:
        response = requests.post(base_url, headers=bing_inverse_headers, files={"image": content}, timeout=60)
        data = response.json()
        return data
    except Exception as e:
        return data
    
def get_bing_inverse_data(data):
    responses = []
    try:
        if 'tags' in data.keys():
            tags = data['tags']
            for tag in tags:
                if 'actions' in tag.keys():
                    for action in tag['actions']:
                        if action['actionType'] == 'VisualSearch' and 'data' in action.keys():
                            for value in action['data']['value']:
                                if "hostPageUrl" in value.keys():
                                    try:
                                        response = requests.get(value['hostPageUrl'], headers=headers, timeout=60)
                                        soup = BeautifulSoup(response.content, 'html.parser')
                                        responses.append({"url": value['hostPageUrl'], "text": soup.get_text()})
                                    except:
                                        continue
        return responses
    except Exception as e:
        return responses

def get_google_inverse_data(data):
    responses = []
    try:
        if 'pages_with_matching_images' in data.keys():
            for page in data['pages_with_matching_images']:
                try:
                    response = requests.get(page['url'], headers=headers, timeout=60)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    responses.append({"url": page['url'], "text": soup.get_text()})
                except:
                    continue
        return responses
    except Exception as e:
        return responses
    
def get_data(caption, img_content):
    entities = get_entities(caption)
    if len(entities) == 0:
        query = caption
    else:
        query = create_query(entities)
    wikipedia_search = get_wikipedia_data(query)
    google_search = get_google_data(query)
    bing_search = get_bing_search_results(query)
    inverse_google_search = get_inverse_image_response(img_content)
    inverse_bing_search = get_bing_image_response(img_content)
    inverse_google_data = get_google_inverse_data(inverse_google_search)
    inverse_bing_data = get_bing_inverse_data(inverse_bing_search)
    return wikipedia_search, google_search, bing_search, inverse_google_search, inverse_bing_search, inverse_google_data, inverse_bing_data