
import requests
from typing import Dict, List


FB_BEARER_TOKEN = "EAAPU4Y5G2QgBO9JsZAyXXXuRWXrNdsENglbbCQHZBbjV7lYiTRzvl1gxHQsgK8RPCwX0EZApQj9Dpzs9Mt9FLoqmi8WNwYwZCwe3MA0fg5oZCbAUsOU3TS7YT5gYGsl1PSneMbK8jzYYJn2ZBD6qUqUPIVyPWO1ZBxa0DRIHd5W9k6xOMB7N7gzIM9AZAwBCHzN1VLzcqBGrZAyKS2i6aFRG61T0IZCi9a"


def download_media(id: str):
    url = f"https://graph.facebook.com/v19.0/{id}/"
    headers = {
        "Authorization": f"Bearer {FB_BEARER_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        url = response.json()['url']
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(f"media/{id}.jpg", "wb") as f:
                f.write(response.content)
            return id
    return None


def get_text(body: Dict) -> str:
    for entry in body.get('entry', []):
        for change in entry.get('changes', []):
            messages = change.get('value', {}).get('messages', [])
            for message in messages:
                if message.get('type') == 'text':
                    text_body = message.get('text', {}).get('body', '')
                    if text_body:
                        return text_body
    return ""


def get_phone(body: Dict) -> str:
    """
    Extracts and returns the user's phone number from the incoming request body.

    :param body: The incoming request body as a dictionary.
    :return: The user's phone number as a string, or an empty string if not found.
    """
    for entry in body.get('entry', []):
        for change in entry.get('changes', []):
            messages = change.get('value', {}).get('messages', [])
            for message in messages:
                phone_number = message.get('from', '')
                if phone_number:
                    return phone_number
    return ""


def get_media(body: Dict) -> List[str]:
    image_ids = []
    for entry in body.get('entry', []):
        for change in entry.get('changes', []):
            messages = change.get('value', {}).get('messages', [])
            for message in messages:
                if message.get('type') == 'image':
                    image_id = message.get('image', {}).get('id', '')
                    if image_id:
                        image_ids.append(image_id)
    downloaded = [download_media(id) for id in image_ids]
    return [d for d in downloaded if d is not None]
