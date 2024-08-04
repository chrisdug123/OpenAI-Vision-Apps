import base64
from django.conf import settings
from openai import OpenAI
import base64
import requests
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_tags(description):
    doc = nlp(description)
    tags = set([token.lemma_ for token in doc if token.pos_ in ['NOUN','ADJ']])
    return list(tags)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_with_openai(image_path):
    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
    }
    payload = {
        "model" : "gpt-4o-mini",
        "messages":[
            {
                "role":"user",
                "content":[
                    {
                        "type": "text",
                        "text": "What's in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64, {base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions",headers=headers,json=payload)
    
    description = response.json()['choices'][0]['message']['content']
    tags = extract_tags(description)
    return tags