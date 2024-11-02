# Core app logic Py3 & Flask

from flask import Flask, request, jsonify
from google.cloud import pubsub_v1, bigquery
import os

app = Flask(__name__)

# Initialize Pub/Sub and BigQuery clients
pubsub_client = pubsub_v1.PublisherClient()
bigquery_client = bigquery.Client()

# Load environment variables
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")

@app.route('/')
def index():
    return "Welcome to the Google App Engine Real-Time Analytics Application!"

@app.route('/publish', methods=['POST'])
def publish():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Publish data to Pub/Sub
    data_str = str(data)
    topic_path = pubsub_client.topic_path(os.getenv('GOOGLE_CLOUD_PROJECT'), PUBSUB_TOPIC.split('/')[-1])
    pubsub_client.publish(topic_path, data_str.encode("utf-8"))
    
    return jsonify({"message": "Data published to Pub/Sub"}), 200

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Insert data into BigQuery
    table = bigquery_client.get_table(BIGQUERY_TABLE)
    rows_to_insert = [data]
    errors = bigquery_client.insert_rows_json(table, rows_to_insert)

    if errors:
        return jsonify({"error": "Error inserting into BigQuery", "details": errors}), 500

    return jsonify({"message": "Data processed and stored in BigQuery"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
