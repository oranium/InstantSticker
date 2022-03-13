import requests
import stickerify
from credentials import CREDENTIALS

AZURE_LINK = CREDENTIALS["AZURE_LINK"]


def get_image_info(url):
    r = requests.post(AZURE_LINK + url)
    return r.json()

def get_sticker_from_photo(url):
    image_info = get_image_info(url)

    if ('emotion' in image_info):
        max_val = 0
        for key, value in image_info['emotion'].items():
            if max_val < value:
                (max_val, emotion) = (value, key)
    else:
        emotion = "not_detected"

    if ('faceRectangle' in image_info):
        coords = image_info['faceRectangle']
    else:
        coords = None
    
    image_path = stickerify.sticker_from_rectangle(coords, url)

    return {
        "path": image_path,
        "emotion": emotion,
    }
