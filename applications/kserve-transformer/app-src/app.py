import json
import os
import requests
from flask import Flask, jsonify, request, render_template
from preprocessing import process_data, process_payload
import logging
from kafka import KafkaProducer
from datetime import datetime
import time

application = Flask(__name__)
INFERENCE_ENDPOINT = os.environ.get("INFERENCE_ENDPOINT") or "https://modelmesh-serving.mnist.svc.cluster.local:8008"
USE_OAUTH_PROXY = True if os.environ.get("USE_OAUTH_PROXY") == "true" else False
OAUTH_TOKEN = os.environ.get("OAUTH_TOKEN")
DEBUG = os.environ.get("FLASK_DEBUG")
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP") or "mnist-streaming-cluster-kafka-bootstrap.streaming.svc.cluster.local:9092"
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC") or "mnist-scoring-results"

if USE_OAUTH_PROXY and bool(OAUTH_TOKEN):
    headers = {'Authorization': f'Bearer {OAUTH_TOKEN}'}
else:
    headers = {}

@application.route('/', methods=['GET'])
def status():
    return jsonify({'status': 'ok'})

def write_to_kafka(img_str, prediction):
    # Write maximal score index to kafka topic
    producer = KafkaProducer(bootstrap_servers=[KAFKA_BOOTSTRAP], value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    ts = time.time()
    timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    # Max index is the model prediciton
    index_max = max(range(len(prediction)), key=prediction.__getitem__)
    producer.send(KAFKA_TOPIC, {'time': timestamp,'score': max(prediction), 'prediction': index_max,'png': img_str})
    application.logger.info(f"Producer: {producer}")

@application.route('/', methods=['POST'])
def predict():
    content_type = request.headers.get('Content-Type')
    application.logger.info(f"Content-Type: {content_type}")
    application.logger.info(f"Incoming json: {request.json}")
    img_str = request.json["png"]
    application.logger.info(f"PNG in base64: {img_str}")
    # Process the data adding the request origin
    # Kafka origin => Dark images => Inverse color
    provider = request.json.get("provider") or "webapp"
    application.logger.info(f"Provider: {provider}")
    data = process_data(img_string=img_str, provider=provider)
    application.logger.info(f"Processed data: {data[0]}")
    payload = process_payload(data[0])
    payload = json.dumps(payload)
    application.logger.info(f"Payload: {payload}")
    if DEBUG:
        return jsonify({"status": "OK"})
    r = requests.post(INFERENCE_ENDPOINT, data = payload, headers = headers ,verify = False)
    resp = r.json()
    application.logger.info(f"ModelMesh request response code: {r.status_code}")
    application.logger.info(f"JSON response: {resp}")
    print(resp)
    prediction = resp['outputs'][0]['data']
    if provider == "kafka":
        write_to_kafka(img_str, prediction)
        return jsonify({"status": "OK"})
    return jsonify({"data": prediction})

if __name__ == '__main__':
    print(f"Using INFERENCE_ENDPOINT: {INFERENCE_ENDPOINT}")
    print("Change INFERENCE_ENDPOINT env var if needed.")
    print(f"headers: {headers}")
    application.logger.setLevel(logging.INFO)
    application.run(host='0.0.0.0',port=8080)