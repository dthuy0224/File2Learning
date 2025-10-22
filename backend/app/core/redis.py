# app/core/redis.py
import redis
from app.core.config import settings
from urllib.parse import urlparse

redis_url = getattr(settings, "REDIS_URL", None)
if not redis_url:
    raise RuntimeError("REDIS_URL not configured")

# simple redis client
redis_client = redis.from_url(redis_url, decode_responses=True)
