# surrogate_servers/api.py
from flask import Flask, request, jsonify, send_file
from cache_manager import LRUCache
import os
import requests
import asyncio
from kademlia.network import Server
import json  # Added import

app = Flask(__name__)

# Initialize LRU Cache
cache = LRUCache(capacity=10)

# Directory to store cached content
CACHE_DIR = 'cache'
os.makedirs(CACHE_DIR, exist_ok=True)

# Origin Server URL
ORIGIN_SERVER_URL = 'http://cdn-origin:5000'

# Initialize DHT server
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
dht_server = Server()

async def start_dht_node():
    await dht_server.listen(8469)
    await dht_server.bootstrap([('cdn-origin', 8468)])  # Bootstrap with Origin Server DHT node

loop.run_until_complete(start_dht_node())

# Register this surrogate server in the DHT
SURROGATE_SERVER_URL = 'localhost:5001'  # Change if running on a different host or port

async def register_with_dht(content_id):
    # Get existing list of surrogate servers for the content
    value = await dht_server.get(content_id)
    if value is not None:
        # Deserialize the JSON string back to a list
        servers = json.loads(value)
    else:
        servers = []
    if SURROGATE_SERVER_URL not in servers:
        servers.append(SURROGATE_SERVER_URL)
        # Serialize the list before storing
        await dht_server.set(content_id, json.dumps(servers))

@app.route('/content/<content_id>', methods=['GET'])
def get_content(content_id):
    """
    Serve content to the client. If not in cache, fetch from Origin Server.
    """
    cached_file_path = os.path.join(CACHE_DIR, content_id)
    if cache.get(content_id) and os.path.exists(cached_file_path):
        # Cache hit
        return send_file(cached_file_path, as_attachment=True)
    else:
        # Cache miss
        origin_response = requests.get(f"{ORIGIN_SERVER_URL}/content/{content_id}", stream=True)
        if origin_response.status_code == 200:
            # Save content to cache
            with open(cached_file_path, 'wb') as f:
                for chunk in origin_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            # Update cache
            cache.put(content_id, True)
            # Register this surrogate server for the content in the DHT
            loop.run_until_complete(register_with_dht(content_id))
            return send_file(cached_file_path, as_attachment=True)
        else:
            return jsonify({'error': 'Content not found on Origin Server'}), 404

@app.route('/invalidate/<content_id>', methods=['POST'])
def invalidate_content(content_id):
    """
    Endpoint to invalidate cached content.
    """
    cached_file_path = os.path.join(CACHE_DIR, content_id)
    if os.path.exists(cached_file_path):
        os.remove(cached_file_path)
        # Remove from cache
        cache.get(content_id)
    return jsonify({'status': f'Content {content_id} invalidated'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
