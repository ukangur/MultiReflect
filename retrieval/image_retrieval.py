import spacy
import requests
import json
import os
from googleapiclient.discovery import build

nlp = spacy.load('en_core_web_sm')
client_id = "aa5d1f1bde5130ebe33627a614f93689"
client_secret = "833a0ae66e7338af93287b7ce65367c585b75019"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJhYTVkMWYxYmRlNTEzMGViZTMzNjI3YTYxNGY5MzY4OSIsImp0aSI6ImY1NWFjYTg3MzhjMTEwYTA1MzNmMjA2YzEyZjAxNzhjYWVjMmIxMTRlZDJjOWFlNzg4ODY0NTA1ZTk1ZjQyNTM1YTNjYTBlODM3NGJhZTA3IiwiaWF0IjoxNzEwMjQzMDY4LjMyMjE3NywibmJmIjoxNzEwMjQzMDY4LjMyMjE4MiwiZXhwIjozMzI2NzE1MTg2OC4zMjAzMywic3ViIjoiNzUxODM3ODAiLCJpc3MiOiJodHRwczovL21ldGEud2lraW1lZGlhLm9yZyIsInJhdGVsaW1pdCI6eyJyZXF1ZXN0c19wZXJfdW5pdCI6NTAwMCwidW5pdCI6IkhPVVIifSwic2NvcGVzIjpbImJhc2ljIl19.vnKk4E40Vg_7Qy3CR1vTo0H9cWL3xzauiMgydLoPPHjl4ZHMFmgMolE_5EmRoeqJPnbjpTrw8UkL6OOB0QOht8POiUx9MmKSR9Es_KDrQZPt2y8ThUX0sO4v-6VxwE3Re70vp_PQdw9g4WgTUQxWHpYQXzkHHmThhjHKtSekd2CpHkgPvFycyI8fF3lVlvu3sAcTrJpVQGCOwHPnIa-wn6bUKkNoGiLoM1GTp6hKf36uGXb-tKqf1DtueeAg_tG1yZ7qAgYJ53nihZXn5jPJJt-KdOxO83g4aLxZ87cOIhWU03DLP1dQC7Kn8EHHBtUGQ_upyWx7ruIq3ljaqAST8SHOZ2w_EqDs2JCD60pH-q7SfknKoMppTPwZ8_3e-hf7B6KQ8877_iEh496Xb7RoeswFleGj82P2h-ETAIQIURQpPoU4InmRZYRPXvxQrlCTBgUtdM2vgA5spRlyKjJBBDZ5fsRjX93_9qKHIC3SO9TL3MGlSgv7BNs0qofuj2lvY1d8BQIgjA8hsXo8Us0NLaXanppUcZbh3xrozRDdbUHqZLlyuqnDGq9l1hipimvcdTawGUZ0x7kKJKRS8-rsErJtExTabOX-sohCNrLqOwf5Rr4jgWHZa6QrbRNhasCNaVH_UgM_5PpnwJgxZOuEUzTbR2n8VFvfeUIJ3p0th-c"
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36 Edg/122.0.0.0', 'Referer': 'https://www.google.com/'}

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

def get_google_images(caption):
    entities = get_entities(caption)
    if len(entities) == 0:
        query = caption
    else:
        query = create_query(entities)
    # url = "https://www.googleapis.com/customsearch/v1?key=AIzaSyCXi8wXOFREwIwDZ0B4OqD5L2EKSmyoo_M&cx=b7f8c7d4cce094056&q=" + query + "&searchType=image"
    try:
        service = build("customsearch", "v1", developerKey = "AIzaSyCXi8wXOFREwIwDZ0B4OqD5L2EKSmyoo_M")
        res = service.cse().list(q=query,cx="b7f8c7d4cce094056",searchType="image").execute()
        # response = requests.get(url)
        # data = response.json()
        return res
    except Exception as e:
        return {}

def get_commons_response(caption):
    entities = get_entities(caption)
    responses = {}
    try:
        if len(entities) > 0:
            for ent in entities:
                query = ent[0]
                url = f"https://api.wikimedia.org/core/v1/commons/search/title"
                params = {'q': query, 'limit': 10}
                try:
                    response = requests.get(url, headers={"User-Agent": "Evidence (diwankrish.17@gmail.com)", "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJhYTVkMWYxYmRlNTEzMGViZTMzNjI3YTYxNGY5MzY4OSIsImp0aSI6IjBiZTFmZjQ4YWE5NTlmYTMxYzYwZjhlNTRlNmMyMjcwMDQ4YjEwOGUwYTRjNTI1ZjI5YmVlODJkODI2OWFmMTg2ODgzYWYwYTQyOTZiYjI4IiwiaWF0IjoxNzE0Mzg0Mzc4LjU1NjY1LCJuYmYiOjE3MTQzODQzNzguNTU2NjU0LCJleHAiOjMzMjcxMjkzMTc4LjU1MzYsInN1YiI6Ijc1MTgzNzgwIiwiaXNzIjoiaHR0cHM6Ly9tZXRhLndpa2ltZWRpYS5vcmciLCJyYXRlbGltaXQiOnsicmVxdWVzdHNfcGVyX3VuaXQiOjUwMDAsInVuaXQiOiJIT1VSIn0sInNjb3BlcyI6WyJiYXNpYyJdfQ.AqZIB4TsBqKuKZT7CdLaKINmjyVr1ow-ozTk3kzB1OnJIuC64NBjCM0xkWuTGMJCtBCaaEQ6hyl1_kAYowIxleyjlwgI4epT5Rrx57xr4D6wwNLoBfQmmoFQJTYZ63VlR0Rk_VnDPAky8efmATpPflAfoHbw4YGyquxcFBp3lDiLDR92MpCTroWNVNiM4pDYKs3cfSVB447YcbjCx5Dz8yFwber0rCr6FCMARI7zvdUNAom76_LSw-6xaVX_dgqLAXmigl_Fyj5Qh4XDFX65yvwV3h1lRyAGyH_1-_iifE_PWU9cY7V6oRMgg0n4qlJUr2CTGtcnpsTr4CQs-BmqXJArfIpLghVbZjOflOuvZc3fmDpsRvJbte1aRAtJSRWXe8aRtusdtPQgme4WANnluKUGuiLhd6tCt1kLbnNneZCTmnVPssYwm_yfEidPIEGF7jQxZFjxQ2ESjROhXESbhnQJi2f7LDSt7Q7apzrTSVdbmY75OFae2erGwVFTlvWesSNd46cceLujT-kwhy3FJMo2ioCDX61GVczj389AchFk40EecOzrtCauhbu02aU7ZJEe-D8VMmM4OWUSleBEk0T9wCVM6DBaiaOG2XRSgwilgT6NYF7xYMjEvGlF38JL5vG_3gWBlz5pRByBDavjcLikO06FZ45_fzIpdgB1SLs"}, params=params, timeout=60)
                    data = response.json()
                    responses[query] = data
                except Exception as e:
                    continue
            return responses
        else:
            query = entities
            url = f"https://api.wikimedia.org/core/v1/commons/search/title"
            params = {'q': query, 'limit': 10}
            try:
                response = requests.get(url, headers={"User-Agent": "Evidence (diwankrish.17@gmail.com)", "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJhYTVkMWYxYmRlNTEzMGViZTMzNjI3YTYxNGY5MzY4OSIsImp0aSI6IjBiZTFmZjQ4YWE5NTlmYTMxYzYwZjhlNTRlNmMyMjcwMDQ4YjEwOGUwYTRjNTI1ZjI5YmVlODJkODI2OWFmMTg2ODgzYWYwYTQyOTZiYjI4IiwiaWF0IjoxNzE0Mzg0Mzc4LjU1NjY1LCJuYmYiOjE3MTQzODQzNzguNTU2NjU0LCJleHAiOjMzMjcxMjkzMTc4LjU1MzYsInN1YiI6Ijc1MTgzNzgwIiwiaXNzIjoiaHR0cHM6Ly9tZXRhLndpa2ltZWRpYS5vcmciLCJyYXRlbGltaXQiOnsicmVxdWVzdHNfcGVyX3VuaXQiOjUwMDAsInVuaXQiOiJIT1VSIn0sInNjb3BlcyI6WyJiYXNpYyJdfQ.AqZIB4TsBqKuKZT7CdLaKINmjyVr1ow-ozTk3kzB1OnJIuC64NBjCM0xkWuTGMJCtBCaaEQ6hyl1_kAYowIxleyjlwgI4epT5Rrx57xr4D6wwNLoBfQmmoFQJTYZ63VlR0Rk_VnDPAky8efmATpPflAfoHbw4YGyquxcFBp3lDiLDR92MpCTroWNVNiM4pDYKs3cfSVB447YcbjCx5Dz8yFwber0rCr6FCMARI7zvdUNAom76_LSw-6xaVX_dgqLAXmigl_Fyj5Qh4XDFX65yvwV3h1lRyAGyH_1-_iifE_PWU9cY7V6oRMgg0n4qlJUr2CTGtcnpsTr4CQs-BmqXJArfIpLghVbZjOflOuvZc3fmDpsRvJbte1aRAtJSRWXe8aRtusdtPQgme4WANnluKUGuiLhd6tCt1kLbnNneZCTmnVPssYwm_yfEidPIEGF7jQxZFjxQ2ESjROhXESbhnQJi2f7LDSt7Q7apzrTSVdbmY75OFae2erGwVFTlvWesSNd46cceLujT-kwhy3FJMo2ioCDX61GVczj389AchFk40EecOzrtCauhbu02aU7ZJEe-D8VMmM4OWUSleBEk0T9wCVM6DBaiaOG2XRSgwilgT6NYF7xYMjEvGlF38JL5vG_3gWBlz5pRByBDavjcLikO06FZ45_fzIpdgB1SLs"}, params=params, timeout=60)
                data = response.json()
                responses[query] = data
            except Exception as e:
                pass
            return responses
    except Exception as e:
        return responses
    
def get_bing_responses(caption):
    entities = get_entities(caption)
    if len(entities) > 0:
        query = create_query(entities, "+")
    else:
        query = entities
    url = "https://api.bing.microsoft.com/v7.0/images/search"
    headers = {
        "Content-Type": "multipart/form-data",
        "Ocp-Apim-Subscription-Key": "929c5b48185c49238f06ef8ce0bfe4a9",
    }
    try:
        response = requests.get(url, headers=headers, params={"q": query, "count": 10}, timeout=60)
        data = response.json()
        return data
    except Exception as e:
        return {}
    
def download_google_images(data, file_name):
    if 'items' in data.keys():
        for idx, item in enumerate(data['items']):
            try:
                response = requests.get(item['link'], timeout=60)
                if not os.path.exists(f'./data/retrieved/{file_name}/images/google_images'):
                    os.makedirs(f'./data/retrieved/{file_name}/images/google_images')
                extension = ''
                if 'jpg' in item['link'].split('.')[-1]:
                    extension = 'jpg'
                elif 'png' in item['link'].split('.')[-1]:
                    extension = 'png'
                elif 'jpeg' in item['link'].split('.')[-1]:
                    extension = 'jpeg'
                else:
                    continue
                with open(f'./data/retrieved/{file_name}/images/google_images/{idx+1}.{extension}', 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                continue

def download_commons_images(data, file_name):
    for value in data.values():
        if 'pages' in value.keys():
            for page in value['pages']:
                url = f"https://api.wikimedia.org/core/v1/commons/file/{page['title']}"
                try:
                    response = requests.get(url, headers={"User-Agent": "Evidence (diwankrish.17@gmail.com)", "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJhYTVkMWYxYmRlNTEzMGViZTMzNjI3YTYxNGY5MzY4OSIsImp0aSI6IjBiZTFmZjQ4YWE5NTlmYTMxYzYwZjhlNTRlNmMyMjcwMDQ4YjEwOGUwYTRjNTI1ZjI5YmVlODJkODI2OWFmMTg2ODgzYWYwYTQyOTZiYjI4IiwiaWF0IjoxNzE0Mzg0Mzc4LjU1NjY1LCJuYmYiOjE3MTQzODQzNzguNTU2NjU0LCJleHAiOjMzMjcxMjkzMTc4LjU1MzYsInN1YiI6Ijc1MTgzNzgwIiwiaXNzIjoiaHR0cHM6Ly9tZXRhLndpa2ltZWRpYS5vcmciLCJyYXRlbGltaXQiOnsicmVxdWVzdHNfcGVyX3VuaXQiOjUwMDAsInVuaXQiOiJIT1VSIn0sInNjb3BlcyI6WyJiYXNpYyJdfQ.AqZIB4TsBqKuKZT7CdLaKINmjyVr1ow-ozTk3kzB1OnJIuC64NBjCM0xkWuTGMJCtBCaaEQ6hyl1_kAYowIxleyjlwgI4epT5Rrx57xr4D6wwNLoBfQmmoFQJTYZ63VlR0Rk_VnDPAky8efmATpPflAfoHbw4YGyquxcFBp3lDiLDR92MpCTroWNVNiM4pDYKs3cfSVB447YcbjCx5Dz8yFwber0rCr6FCMARI7zvdUNAom76_LSw-6xaVX_dgqLAXmigl_Fyj5Qh4XDFX65yvwV3h1lRyAGyH_1-_iifE_PWU9cY7V6oRMgg0n4qlJUr2CTGtcnpsTr4CQs-BmqXJArfIpLghVbZjOflOuvZc3fmDpsRvJbte1aRAtJSRWXe8aRtusdtPQgme4WANnluKUGuiLhd6tCt1kLbnNneZCTmnVPssYwm_yfEidPIEGF7jQxZFjxQ2ESjROhXESbhnQJi2f7LDSt7Q7apzrTSVdbmY75OFae2erGwVFTlvWesSNd46cceLujT-kwhy3FJMo2ioCDX61GVczj389AchFk40EecOzrtCauhbu02aU7ZJEe-D8VMmM4OWUSleBEk0T9wCVM6DBaiaOG2XRSgwilgT6NYF7xYMjEvGlF38JL5vG_3gWBlz5pRByBDavjcLikO06FZ45_fzIpdgB1SLs"}, timeout=60)
                    response = response.json()
                    if 'preferred' in response.keys():
                        new_url = response['preferred']['url']
                        new_response = requests.get(new_url, headers={"User-Agent": "Evidence (diwankrish.17@gmail.com)", "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJhYTVkMWYxYmRlNTEzMGViZTMzNjI3YTYxNGY5MzY4OSIsImp0aSI6IjBiZTFmZjQ4YWE5NTlmYTMxYzYwZjhlNTRlNmMyMjcwMDQ4YjEwOGUwYTRjNTI1ZjI5YmVlODJkODI2OWFmMTg2ODgzYWYwYTQyOTZiYjI4IiwiaWF0IjoxNzE0Mzg0Mzc4LjU1NjY1LCJuYmYiOjE3MTQzODQzNzguNTU2NjU0LCJleHAiOjMzMjcxMjkzMTc4LjU1MzYsInN1YiI6Ijc1MTgzNzgwIiwiaXNzIjoiaHR0cHM6Ly9tZXRhLndpa2ltZWRpYS5vcmciLCJyYXRlbGltaXQiOnsicmVxdWVzdHNfcGVyX3VuaXQiOjUwMDAsInVuaXQiOiJIT1VSIn0sInNjb3BlcyI6WyJiYXNpYyJdfQ.AqZIB4TsBqKuKZT7CdLaKINmjyVr1ow-ozTk3kzB1OnJIuC64NBjCM0xkWuTGMJCtBCaaEQ6hyl1_kAYowIxleyjlwgI4epT5Rrx57xr4D6wwNLoBfQmmoFQJTYZ63VlR0Rk_VnDPAky8efmATpPflAfoHbw4YGyquxcFBp3lDiLDR92MpCTroWNVNiM4pDYKs3cfSVB447YcbjCx5Dz8yFwber0rCr6FCMARI7zvdUNAom76_LSw-6xaVX_dgqLAXmigl_Fyj5Qh4XDFX65yvwV3h1lRyAGyH_1-_iifE_PWU9cY7V6oRMgg0n4qlJUr2CTGtcnpsTr4CQs-BmqXJArfIpLghVbZjOflOuvZc3fmDpsRvJbte1aRAtJSRWXe8aRtusdtPQgme4WANnluKUGuiLhd6tCt1kLbnNneZCTmnVPssYwm_yfEidPIEGF7jQxZFjxQ2ESjROhXESbhnQJi2f7LDSt7Q7apzrTSVdbmY75OFae2erGwVFTlvWesSNd46cceLujT-kwhy3FJMo2ioCDX61GVczj389AchFk40EecOzrtCauhbu02aU7ZJEe-D8VMmM4OWUSleBEk0T9wCVM6DBaiaOG2XRSgwilgT6NYF7xYMjEvGlF38JL5vG_3gWBlz5pRByBDavjcLikO06FZ45_fzIpdgB1SLs"}, timeout=60)
                        if not os.path.exists(f'./data/retrieved/{file_name}/images/commons_images'):
                            os.makedirs(f'./data/retrieved/{file_name}/images/commons_images')
                        extension = new_url.split('.')[-1]
                        with open(f'./data/retrieved/{file_name}/images/commons_images/{page["id"]}.{extension}', 'wb') as f:
                            f.write(new_response.content)
                except Exception as e:
                    continue
                
def download_bing_images(data, file_name):
    if 'value' in data.keys():
        for value in data['value']:
            try:
                response = requests.get(value['contentUrl'], headers=headers, timeout=60)
                if not os.path.exists(f'./data/retrieved/{file_name}/images/bing_images'):
                    os.makedirs(f'./data/retrieved/{file_name}/images/bing_images')
                if "encodingFormat" in value.keys():
                    extension = value["encodingFormat"]
                else:
                    extension = value['contentUrl'].split('.')[-1]
                with open(f'./data/retrieved/{file_name}/images/bing_images/{value["imageId"]}.{extension}', 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                continue
    
def get_image_data(caption, idx):
    google_data = get_google_images(caption)
    bing_data = get_bing_responses(caption)
    commons_data = get_commons_response(caption)
    download_google_images(google_data, idx)
    download_commons_images(commons_data, idx)
    download_bing_images(bing_data, idx)
    return google_data, bing_data, commons_data