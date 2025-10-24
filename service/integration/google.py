import time
from typing import Union, List

import httpx
import os
from fastapi import status, HTTPException
from core.dependencies import HTTPClient
from core.logger import logger
from schema.integration.google import PlacesResponse, PlacePredictionResponse, GooglePlaceDetailsResponse, \
    BusinessPlaceDetailsResponse, GooglePlaceDetailsResult

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
PLACES_BASE_URL = os.getenv("GOOGLE_PLACES_BASE_URL")

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

