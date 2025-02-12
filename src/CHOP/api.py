import base64
import requests
import httpx

API_RUL= ''

httpx_client = httpx.Client(verify=False)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def inference_chat(chat, API_TOKEN):    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }

    data = {
        "model": 'gpt-4o',
        "messages": [],
        "max_tokens": 4096,
        "temperature": 0,
    }

    for role, content in chat:
        data["messages"].append({"role": role, "content": content})

    while 1:
        try:
            res = requests.post(API_RUL, headers=headers, json=data)
            print(res)
            res = res.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Network Error: {str(e)}")
        else:
            break
    return res
