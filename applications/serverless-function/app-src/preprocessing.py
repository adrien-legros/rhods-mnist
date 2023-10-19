import io
import os
import re
import base64
import json
import numpy as np
from PIL import Image

MODEL_VERSION = os.environ.get("MODEL_VERSION") or "v2"

def process_data(img_string, provider):
    if provider == "webapp":
        img_str = re.search(r'base64,(.*)', img_string).group(1)
        image_bytes = io.BytesIO(base64.b64decode(img_str))
        im = Image.open(image_bytes)
        arr = np.array(im)[:,:,0:1]
        arr = (255 - arr) / 255
    elif provider == "kafka":
        img_str = img_string
        image_bytes = io.BytesIO(base64.b64decode(img_str))
        im = Image.open(image_bytes)
        arr = np.array(im)[:,:]
        arr = 1 - ((255 - arr) / 255)
    else:
        raise Exception(f"Provider {provider} not implemented.")
    print(arr.shape)
    res = arr.reshape(1,-1).tolist()
    return res

def process_payload(data):
    if MODEL_VERSION == "v1":
        file_path = "./input_template/v1.json"
    else:
        file_path = "./input_template/v2.json"
    f = open(file_path)
    payload = json.load(f)
    payload['inputs'][0]['data'] = data
    return payload