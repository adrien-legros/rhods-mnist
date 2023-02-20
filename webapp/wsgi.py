import json
import os
import requests
from flask import Flask, jsonify, request, render_template
from preprocessing import process_data, process_payload

application = Flask(__name__)
INFERENCE_ENDPOINT = os.environ.get("INFERENCE_ENDPOINT") or "localhost:8008"

@application.route('/')
def index():
    return render_template('index.html') 

@application.route('/status')
def status():
    return jsonify({'status': 'ok'})

# def call_mm(img_input):

#     requests.post(MM_URL, data=)
#     res = {"data": [0, 1 ,0, 0, 0, 0, 0, 0, 0, 0]}
#     return res

@application.route('/predict', methods=['POST'])
def predict():
    img_str = request.json["draw"]
    data = process_data(img_str)
    payload = process_payload(data[0])
    payload = json.dumps(payload)
    r = requests.post(INFERENCE_ENDPOINT, data = payload, verify = False)
    resp = r.json()
    print(resp)
    prediction = resp['outputs'][0]['data']
    return jsonify({"data": prediction})