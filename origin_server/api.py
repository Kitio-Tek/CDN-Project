# origin_server/api.py
from flask import Flask, request, jsonify, send_file
import asyncio
from dht_node import start_dht_node
import os
import json  # Added import
import requests  # Added import

app = Flask(__name__)

# Initialize DHT server
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
dht_server = loop.run_until_complete(start_dht_node())

# Directory to store uploaded content
CONTENT_DIR = 'content'
os.makedirs(CONTENT_DIR, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_content():
    """
    Endpoint to upload new content to the Origin Server.
    Expects 'content_id' and 'file' in the form data.
    """
    if 'content_id' not in request.form or 'file' not in request.files:
        return jsonify({'error': 'Missing content_id or file'}), 400

    content_id = request.form['content_id']
    file = request.files['file']
    file_path = os.path.join(CONTENT_DIR, content_id)

    # Save the file to the content directory
    file.save(file_path)

    # Register content in DHT with an empty list of surrogate servers
    # Serialized using JSON
    loop.run_until_complete(dht_server.set(content_id, json.dumps([])))

    return jsonify({'status': 'Content uploaded successfully'}), 200

@app.route('/content/<content_id>', methods=['GET'])
def get_content(content_id):
    """
    Endpoint to retrieve content from the Origin Server.
    """
    file_path = os.path.join(CONTENT_DIR, content_id)
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name=content_id
        )
    else:
        return jsonify({'error': 'Content not found'}), 404

@app.route('/invalidate/<content_id>', methods=['POST'])
def invalidate_content(content_id):
    """
    Endpoint to invalidate cached content on Surrogate Servers.
    """
    # Fetch list of surrogate servers from DHT
    value = loop.run_until_complete(dht_server.get(content_id))
    if value is not None:
        # Deserialize the JSON string back to a list
        surrogate_servers = json.loads(value)
    else:
        surrogate_servers = []

    # Invalidate cache on all surrogate servers
    for server_url in surrogate_servers:
        try:
            requests.post(f"http://{server_url}/invalidate/{content_id}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to invalidate cache on {server_url}: {e}")

    return jsonify({'status': 'Cache invalidation requests sent'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
