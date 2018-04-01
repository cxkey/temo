from conf import *
import threading
import redis
from tornado.gen import coroutine
from tornado import gen

class Redis:
    _instance_lock = threading.Lock()

    def __init__(self):
        self.redis = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    
    @staticmethod
    def instance():
        if not hasattr(Redis, '_instance'):
            with Redis._instance_lock:
                if not hasattr(Redis, '_instance'):
                    Redis._instance = Redis()
        return Redis._instance

    def get(self, key):
        return self.redis.get(key)

    def delete(self, key):
        return self.redis.delete(key)

    def set(self, key, value, seconds=REDIS_CACHE_PERIOD):
        self.redis.set(key, value, seconds)

    def set_no_expire(self, key, value):
        self.redis.set(key, value)


redis = Redis.instance() 
