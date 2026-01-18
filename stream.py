import os
from openai import OpenAI
import json

with open("config.json","r") as f:
    config = json.load(f)
    
client = OpenAI(
    api_key = config['api_key'],
    base_url = config['base_url']
)

response = client.chat.completions.create(
    model = "intern-s1",
    messages = [{
        "role":"user",
        "content":[
            {
                "type":"text",
                "text":"从左到右，给出图中反应物的化学式"
            },
            {
                "type":"image_url",
                "image_url": 
                    {
                    "url": "https://pic1.imgdb.cn/item/68d23c82c5157e1a882ad47f.png",
                    },
            }
        ]
    }
            ],
    extra_body={
        "thinking_mode": True,
        "temperature": 0.7,
        "top_p": 1.0,
        "top_k": 50,
        "min_p": 0.0,
    },
)

print(response.choices[0].message.content)
        