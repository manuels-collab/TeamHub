import json
from app.extensions import redis_client
# Import the correct Redis exceptions
from redis.exceptions import ConnectionError, TimeoutError

def get_cache(key):
    """Retrieve a value from the cache."""
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except (ConnectionError, TimeoutError) as e:
        print(f"Redis connection error: {e}")
        return None

def set_cache(key, value, ttl):
    """Set a value in the cache with a time to live (TTL)."""
    try:
        serialised_value = json.dumps(value)
        redis_client.setex(key, ttl, serialised_value)
    except (ConnectionError, TimeoutError) as e:
        print(f"Redis connection error: {e}")
    
def delete_cache(key):
    try:
        redis_client.delete(key)
    except (ConnectionError, TimeoutError) as e:
        print(f"Redis connection error: {e}")

def delete_cache_by_pattern(pattern):
    try:
        # Added the '*' wildcard at the end so it catches all related pagination keys
        keys = redis_client.keys(f'{pattern}*')
        if keys:
            redis_client.delete(*keys)
    except (ConnectionError, TimeoutError) as e:
        print(f"Redis connection error: {e}")
