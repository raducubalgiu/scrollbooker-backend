from typing import Union

import httpx

async_client: Union[httpx.AsyncClient, None] = None

def get_http_client() -> httpx.AsyncClient:
    client = async_client
    if client is None:
        raise RuntimeError("HTTP Client not initialized")
    return client

