# cache.py

import redis
import json

class Cache:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def set(self, key, value, expiration=3600):
        self.redis.setex(key, expiration, json.dumps(value))

    def get(self, key):
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None