# surrogate_servers/cache_manager.py
from collections import OrderedDict
import threading

class LRUCache:
    def __init__(self, capacity=100):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            # Move the key to the end to indicate recent use
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                # Move the key to the end to indicate recent use
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                # Pop the first item (least recently used)
                self.cache.popitem(last=False)
