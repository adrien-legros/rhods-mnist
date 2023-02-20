import io
import re
import base64
import json
import numpy as np
from PIL import Image

def process_data(img_string):
    img_str = re.search(r'base64,(.*)', img_string).group(1)
    image_bytes = io.BytesIO(base64.b64decode(img_str))
    im = Image.open(image_bytes)
    arr = np.array(im)[:,:,0:1]
    arr = (255 - arr) / 255
    res = arr.reshape(1,-1).tolist()
    return res

def process_payload(data):
    f = open("./input_template.json")
    payload = json.load(f)
    payload['inputs'][0]['data'] = data
    return payload