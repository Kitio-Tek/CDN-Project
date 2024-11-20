from flask import Flask, send_file
import os
import io
import json
from typing import List, Dict
import time

cache_limit = 3 * 2**20  # 3MB
origin_directory = "origin"
# origin_ip = "http://localhost:5000"
cache_directory = "cache"
cache_index_stored = "cache_index.json"
cache_index: Dict[str, List[Dict]] = {}


def save_cache_index() -> None:
    with open(cache_index_stored, "w") as f:
        f.write(json.dumps(cache_index))


def create_cache_index() -> None:
    global cache_index
    try:
        with open(cache_index_stored, "r") as f:
            cache_index = json.load(f)
        if not cache_index.get("files"):
            cache_index = {}
            cache_index["files"] = []
            save_cache_index()
        # Only add valid files to the cache index
        cache_index["files"] = [
            file
            for file in cache_index["files"]
            if os.path.exists(os.path.join(cache_directory, file["name"]))
        ]
        # Sort files by last used
        cache_index["files"] = sorted(
            cache_index["files"], key=lambda file: file["last_used"], reverse=True
        )
    except Exception:
        cache_index["files"] = []
        save_cache_index()


def get_file_from_origin(filename) -> io.BytesIO:
    # to change if origin is remote
    file_path = os.path.join(origin_directory, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError
    bytes = None
    with open(file_path, "rb") as f:
        bytes = f.read()
        f.seek(0)
    return bytes


def get_file_from_cache(filename) -> io.BytesIO | None:
    file_path = os.path.join(cache_directory, filename)
    bytes = None
    if not os.path.exists(file_path):
        return bytes
    with open(file_path, "rb") as f:
        bytes = f.read()
        f.seek(0)
    return bytes


def get_cache_current_size() -> int:
    cache_size = 0
    for file in os.listdir(cache_directory):
        cache_size += os.path.getsize(os.path.join(cache_directory, file))
    return cache_size


def add_file_in_cache_index(file: Dict) -> None:
    global cache_index
    cache_index["files"].insert(0, file)
    save_cache_index()


def update_file_in_cache_index(index: int) -> None:
    global cache_index
    file: Dict = cache_index["files"].pop(index)
    file["last_used"] = int(time.time())
    cache_index["files"].insert(0, file)
    save_cache_index()


app = Flask(__name__)


@app.route("/download/<filename>")
def download(filename):
    global cache_index

    try:
        index = next(
            (
                i
                for i, file in enumerate(cache_index["files"])
                if file.get("name", False) == filename
            ),
            0,
        )
        path_in_cache = os.path.join(cache_directory, filename)
        bytes: io.BytesIO = get_file_from_cache(filename)

        is_from_origin = bytes is None
        if is_from_origin:
            bytes = get_file_from_origin(filename)

            if len(bytes) > cache_limit:
                return "File too big", 400

            # Last recently used
            cache_is_full: bool = get_cache_current_size() + len(bytes) > cache_limit
            while cache_is_full:
                file_to_remove = cache_index["files"].pop()
                os.remove(os.path.join(cache_directory, file_to_remove["name"]))
                cache_is_full = get_cache_current_size() + len(bytes) > cache_limit

            # Save file in cache
            with open(path_in_cache, "wb") as f:
                f.write(bytes)
            add_file_in_cache_index({"name": filename, "last_used": int(time.time())})

        else:
            update_file_in_cache_index(index)

        return send_file(path_in_cache)

    except FileNotFoundError:
        return "File not found", 404

    except Exception as e:
        print(e)
        return "Internal server error", 500


if __name__ == "__main__":
    create_cache_index()
    app.run(host="0.0.0.0", debug=True)
