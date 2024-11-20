# tests/test_cache_manager.py
import unittest
from surrogate_servers.cache_manager import LRUCache

class TestLRUCache(unittest.TestCase):
    def test_cache(self):
        cache = LRUCache(capacity=2)
        cache.put('a', 1)
        cache.put('b', 2)
        self.assertEqual(cache.get('a'), 1)
        cache.put('c', 3)
        self.assertIsNone(cache.get('b'))
        self.assertEqual(cache.get('c'), 3)

if __name__ == '__main__':
    unittest.main()
