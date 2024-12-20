from flask import Flask, send_file, request
import os
import json
from typing import List, Dict
import time
import requests
from requests_toolbelt.adapters import source
import socket
import fcntl
import struct


def get_ip_address(ifname: str) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(
        fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack("256s", bytes(ifname[:15], "utf-8")),
        )[20:24]
    )


origin_url = "http://1.1.2.1:5000"
surrogate_unicast_address = get_ip_address("eth1")
surrogate_port = 5000
cache_limit = 5 * 2**10  # 5kB
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
        # Sort files from most used to least used
        cache_index["files"] = sorted(
            cache_index["files"], key=lambda file: file["last_used"], reverse=True
        )
    except Exception:
        cache_index["files"] = []
        save_cache_index()


def get_file_from_origin(filename: str) -> bytes:
    src = source.SourceAddressAdapter(surrogate_unicast_address)
    with requests.Session() as session:
        session.mount("http://", src)
        res = session.get(f"{origin_url}/{filename}")
    if res.status_code == 404:
        raise FileNotFoundError
    return res.content


def get_file_from_cache(filename: str) -> bytes | None:
    file_path = os.path.join(cache_directory, filename)
    file = None
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            file = f.read()
            f.seek(0)
    return file


def get_cache_current_size() -> int:
    cache_size = 0
    for file in os.listdir(cache_directory):
        cache_size += os.path.getsize(os.path.join(cache_directory, file))
    return cache_size


def add_file_in_cache_index(filename: str) -> None:
    global cache_index
    file = {"name": filename, "last_used": int(time.time())}
    cache_index["files"].insert(0, file)
    save_cache_index()


def update_file_in_cache_index(index: int) -> None:
    global cache_index
    file: Dict = cache_index["files"].pop(index)
    file["last_used"] = int(time.time())
    cache_index["files"].insert(0, file)
    save_cache_index()


app = Flask(__name__)


@app.route("/<filename>", methods=["GET"])
def download(filename: str):
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
        file_bytes: bytes = get_file_from_cache(filename)

        cache_miss = file_bytes is None
        if cache_miss:
            file_bytes = get_file_from_origin(filename)

            if len(file_bytes) > cache_limit:
                return "File too big", 400

            # Least recently used
            cache_is_full: bool = (
                get_cache_current_size() + len(file_bytes) > cache_limit
            )
            while cache_is_full:
                file_to_remove = cache_index["files"].pop()
                os.remove(os.path.join(cache_directory, file_to_remove["name"]))
                cache_is_full = get_cache_current_size() + len(file_bytes) > cache_limit

            # Save file in cache
            with open(path_in_cache, "wb") as f:
                f.write(file_bytes)
            add_file_in_cache_index(filename)

        else:
            update_file_in_cache_index(index)

        return send_file(path_in_cache)

    except FileNotFoundError:
        return "File not found", 404

    except Exception as e:
        print(e)
        return "Internal server error", 500


@app.route("/<filename>", methods=["DELETE"])
def delete_from_cache(filename: str):
    headers = request.headers
    if headers.get("Authorization") != "Bearer admin":
        return "Unauthorized", 401

    global cache_index
    try:
        index = next(
            (
                i
                for i, file in enumerate(cache_index["files"])
                if file.get("name", False) == filename
            ),
            None,
        )

        # Remove file from cache index
        if index is not None:
            cache_index["files"].pop(index)
            cache_index["files"] = sorted(
                cache_index["files"], key=lambda file: file["last_used"], reverse=True
            )
            save_cache_index()

        # Remove file from cache
        if not os.path.exists(os.path.join(cache_directory, filename)):
            return "File not found", 404
        os.remove(os.path.join(cache_directory, filename))

        return "File removed", 200

    except Exception as e:
        print(e)
        return "Internal server error", 500


if __name__ == "__main__":
    create_cache_index()
    app.run(host="0.0.0.0", port=surrogate_port, debug=True)
