import redis.asyncio as redis
from src.conf.config import config

redis_client = redis.Redis(host=config.REDIS_HOST, port=6379, decode_responses=True)
