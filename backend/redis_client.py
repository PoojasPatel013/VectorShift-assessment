import os
import redis.asyncio as redis
from kombu.utils.url import safequote
from fastapi import HTTPException

# Configure Redis connection
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6380))  # Changed to 6380 to avoid port conflicts
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

# Create Redis client with connection pool
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,  # Automatically decode responses to strings
    socket_timeout=5,      # 5 second timeout
    socket_connect_timeout=5
)

async def add_key_value_redis(key: str, value: str, expire: int = None):
    """Add a key-value pair to Redis with optional expiration"""
    try:
        async with redis_client.client() as client:
            await client.set(key, value)
            if expire:
                await client.expire(key, expire)
            return True
    except redis.exceptions.ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to Redis: {str(e)}")

async def get_value_redis(key: str):
    """Get value from Redis by key"""
    try:
        async with redis_client.client() as client:
            value = await client.get(key)
            return value
    except redis.exceptions.ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting from Redis: {str(e)}")

async def delete_key_redis(key: str):
    """Delete a key from Redis"""
    try:
        async with redis_client.client() as client:
            await client.delete(key)
            return True
    except redis.exceptions.ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting from Redis: {str(e)}")
