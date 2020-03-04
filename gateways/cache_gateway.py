import redis
import logging
import pickle
import json
import aioredis
from settings import REDIS_HOST, REDIS_PORT


log = logging.getLogger(__name__)


class CacheGateway:
    redis_host = REDIS_HOST
    redis_port = REDIS_PORT
    redis_password = ""
    queue = None

    def __init__(self):
        self.queue = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            password="",
        )
        self.pubsub = self.queue.pubsub()

    @staticmethod
    async def get_poll():
        return await aioredis.create_redis_pool(f'redis://{REDIS_HOST}:{REDIS_PORT}')

    def subscribe(self, **kwargs):
        self.pubsub.subscribe(**kwargs)

    def publish_message(self, key, message):
        log.debug(f"publishing in {key}: {message}")
        return self.queue.publish(key, message)

    def close(self):
        self.queue.connection_pool.disconnect()
        self.queue.close()

    def get(self, key, is_json=False, is_pickle=False):
        value = self.queue.get(key)
        if is_json:
            return json.loads(value)
        if is_pickle:
            return pickle.loads(value)
        return value

    def set(self, key, value, is_json=False, is_pickle=False, expires=None):
        if is_json:
            formatted_value = json.dumps(value)
        elif is_pickle:
            formatted_value = pickle.dumps(value)
        else:
            formatted_value = value

        self.queue.set(key, formatted_value)
        if expires:
            self.queue.expire(key, expires)

    def delete(self, key):
        if self.queue.get(key):
            self.queue.delete(key)
