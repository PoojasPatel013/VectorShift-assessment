import os
import redis.asyncio as redis
from kombu.utils.url import safequote
from fastapi import HTTPException
from redis.exceptions import ConnectionError, RedisError

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6380))  
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,  
    socket_timeout=5,      
    socket_connect_timeout=5
)

async def add_key_value_redis(key: str, value: str, expire: int = None):
    try:
        async with redis_client.client() as client:
            await client.set(key, value)
            if expire:
                await client.expire(key, expire)
            return True
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to Redis: {str(e)}")

async def get_value_redis(key: str):
    try:
        async with redis_client.client() as client:
            value = await client.get(key)
            return value
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting from Redis: {str(e)}")

async def delete_key_redis(key: str):
    try:
        async with redis_client.client() as client:
            await client.delete(key)
            return True
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting from Redis: {str(e)}")
