import hashlib
import time
from typing import Union, List, Tuple
from urllib.parse import urlencode

import re
import httpx
import os

from fastapi import status, HTTPException
from starlette.responses import Response

from core.dependencies import HTTPClient, RedisClient
from core.logger import logger
from schema.integration.google import PlacesResponse, PlacePredictionResponse, GooglePlaceDetailsResponse, \
    BusinessPlaceDetailsResponse, GooglePlaceDetailsResult, StaticMapQuery

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
PLACES_BASE_URL = os.getenv("GOOGLE_PLACES_BASE_URL")

STATIC_BASE_URL = os.getenv("GOOGLE_STATIC_MAPS_BASE_URL")
STATIC_MAP_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_EDGE_TTL = 86400 # 24h

async def search_places(
        client: HTTPClient,
        query: str
) -> List[PlacePredictionResponse]:
    url = f"{PLACES_BASE_URL}/autocomplete/json"
    params = {
        "input": query,
        "key": API_KEY,
        "language": "ro",
        "components": "country:ro",
        "location": "44.437,26.104",
        "radius": 25000,
        "strictbounds": "true",
        "types": "geocode",
    }
    t0 = time.perf_counter()
    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Google Autocomplete Error, Query: {query}, url: {url}, Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

    logger.info(
        f"Google Autocomplete OK. Query: {query}, status_code: {resp.status_code}, duration_ms: {round((time.perf_counter() - t0) * 1000, 2)}",
    )
    payload = resp.json()
    google_status = payload.get("status", "OK")

    if google_status not in ("OK", "ZERO_RESULTS"):
        error_message = payload.get("error_message")
        logger.error(f"Google Autocomplete Bad Status. Query: {query}, status_code: {resp.status_code}, error_message: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Google Places returned status={google_status}"
        )

    places = PlacesResponse.model_validate(resp.json())

    return [
        PlacePredictionResponse(
            description=place.description,
            place_id=place.place_id
        )
        for place in places.predictions
    ]

def _get_component(result: GooglePlaceDetailsResult, type_name: str) -> Union[str, None]:
    for c in result.address_components:
        if type_name in c.types:
            return c.long_name
    return None

async def get_place_details(
        client: HTTPClient,
        place_id: str
) -> BusinessPlaceDetailsResponse:
    url = f"{PLACES_BASE_URL}/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_address,geometry,address_components",
        "key": API_KEY,
        "language": "ro"
    }

    t0 = time.perf_counter()
    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Google Details Error, Place id: {place_id}, url: {url}, Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

    dur = round((time.perf_counter() - t0) * 1000, 2)
    logger.bind(event="google_details_http_ok", place_id=place_id,
                status_code=resp.status_code, duration_ms=dur).info("request finished")

    payload = resp.json()
    data = GooglePlaceDetailsResponse.model_validate(payload)

    if data.status not in ("OK",):
        error_message = payload.get("error_message")
        logger.error(f"Google Details Bad Status, Place id: {place_id}, status_code: {data.status}, Error: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Something went wrong"
        )

    assert data.result is not None
    place = data.result

    return BusinessPlaceDetailsResponse(
        place_id=place.place_id or place_id,
        address=place.formatted_address,
        lat=place.geometry.location.lat,
        lng=place.geometry.location.lng,
        country_code=_get_component(place, "country"),
        city=_get_component(place, "locality") or _get_component(place, "administrative_area_level_1"),
        route=_get_component(place, "route"),
        street_number=_get_component(place, "street_number"),
        postal_code=_get_component(place, "postal_code"),
    )

# Static Map
_whitespace = re.compile(r"\s+")

def _norm(values: List[str]) -> List[str]:
    cleaned = [_whitespace.sub("", v) for v in values if v]
    return sorted(cleaned)

def _build_google_params(q: StaticMapQuery) -> List[Tuple[str, str]]:
    params: List[Tuple[str, str]] = []
    if q.address:
        params.append(("center", q.address.strip()))
    else:
        params.append(("center", f"{q.center_lat},{q.center_lng}"))

    params += [
        ("zoom", str(q.zoom)),
        ("size", f"{q.width}x{q.height}"),
        ("scale", str(q.scale)),
        ("maptype", q.maptype),
        ("language", q.language),
        ("key", API_KEY),
    ]

    if q.region:
        params.append(("region", q.region))

    for m in _norm(q.markers):
        params.append(("markers", m))
    for p in _norm(q.path):
        params.append(("path", p))
    for s in _norm(q.style):
        params.append(("style", s))

    return params

def _cache_key(params: List[Tuple[str, str]]) -> str:
    stabilized = sorted(params, key=lambda kv: (kv[0], kv[1]))
    raw = urlencode(stabilized, doseq=True)
    return "staticmap:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

async def fetch_static_map(
    http_client: HTTPClient,
    redis_client: RedisClient,
    query: StaticMapQuery,
) -> Response:
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")

    params = _build_google_params(query)
    key = _cache_key(params)

    if not query.refresh:
        cached_body = await redis_client.get(key + ":body")
        cached_headers = await redis_client.hgetall(key + ":hdr")

        if cached_body and cached_headers:
            content_type = cached_headers.get(b"content-type", b"image/png").decode()
            logger.info(f"[STATIC MAP] Cache HIT - key={key}")
            return Response(
                content=cached_body,
                media_type=content_type,
                headers={
                    "Cache-Control": cached_headers.get(b"cache-control", b"public, max-age=86400, s-maxage=86400").decode(),
                    "ETag": cached_headers.get(b"etag", b"").decode(),
                    "X-Cache": "HIT",
                },
            )

    logger.info(f"[STATIC MAP] Cache MISS - fetching from Google API for key={key}")
    qstr = urlencode(sorted(params, key=lambda kv: (kv[0], kv[1])), doseq=True)
    url = f"{STATIC_BASE_URL}?{qstr}"

    r = await http_client.get(url)
    if r.status_code != 200:
        logger.error(f"[STATIC MAP] Google Error {r.status_code}: {r.text[:200]}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Upstream error {r.status_code}: {r.text[:200]}"
        )

    if len(r.content) > STATIC_MAP_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Static map prea mare")

    ct = r.headers.get("content-type", "image/png")
    cc = r.headers.get("cache-control", f"public, max-age={DEFAULT_EDGE_TTL}, s-maxage={DEFAULT_EDGE_TTL}")
    et = r.headers.get("etag", "")

    pipe = await redis_client.pipeline()
    pipe.setex(key + ":body", DEFAULT_EDGE_TTL, r.content)
    pipe.hset(key + ":hdr", mapping={"content-type": ct, "cache-control": cc, "etag": et})
    pipe.expire(key + ":hdr", DEFAULT_EDGE_TTL)
    await pipe.execute()

    logger.info(f"[STATIC MAP] Cached new image - key={key} - size={len(r.content)} bytes")

    return Response(
        content=r.content,
        media_type=ct,
        headers={
            "Cache-Control": cc,
            "ETag": et,
            "X-Cache": "MISS",
        },
    )