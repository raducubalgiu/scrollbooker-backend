import os
from fastapi import HTTPException, status
from typing import Union

from redis.asyncio import Redis

redis_client: Union[Redis, None] = None

async def init_redis() -> Redis:
    global redis_client

    if redis_client is None:
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Missing REDIS_URL"
            )
        redis_client = Redis.from_url(redis_url, decode_responses=False)
    return redis_client

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None

    # try:
    #     await redis.ping()
    # except Exception as e:
    #     from fastapi import HTTPException, status
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail=f"Redis connection failed: {e}"
    #     )
    # return redis