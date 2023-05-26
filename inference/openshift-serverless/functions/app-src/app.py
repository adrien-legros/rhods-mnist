import json
import os
import requests
from flask import Flask, jsonify, request, render_template
from preprocessing import process_data, process_payload

application = Flask(__name__)
INFERENCE_ENDPOINT = os.environ.get("INFERENCE_ENDPOINT") or "https://modelmesh-serving.mnist.svc.cluster.local:8008"
USE_OAUTH_PROXY = True if os.environ.get("USE_OAUTH_PROXY") == "true" else False
OAUTH_TOKEN = os.environ.get("OAUTH_TOKEN")

if USE_OAUTH_PROXY and bool(OAUTH_TOKEN):
    headers = {'Authorization': f'Bearer {OAUTH_TOKEN}'}
else:
    headers = {}

@application.route('/', methods=['GET'])
def status():
    return jsonify({'status': 'ok'})

@application.route('/', methods=['POST'])
def predict():
    img_str = request.json["png"]
    data = process_data(img_str)
    payload = process_payload(data[0])
    payload = json.dumps(payload)
    r = requests.post(INFERENCE_ENDPOINT, data = payload, headers = headers ,verify = False)
    resp = r.json()
    print(resp)
    prediction = resp['outputs'][0]['data']
    return jsonify({"data": prediction})

if __name__ == '__main__':
    print(f"Using INFERENCE_ENDPOINT: {INFERENCE_ENDPOINT}")
    print("Change INFERENCE_ENDPOINT env var if needed.")
    print(f"headers: {headers}")
    application.run(host='0.0.0.0',port=8080)