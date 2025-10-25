from typing import List, Optional
from fastapi import APIRouter, Query, Depends

from core.dependencies import HTTPClient, RedisClient
from schema.integration.google import PlacePredictionResponse, BusinessPlaceDetailsResponse, StaticMapQuery
from service.integration.google import search_places, get_place_details, fetch_static_map

router = APIRouter(tags=["Google"])

@router.get("/places",
            summary='Search Google places',
            response_model=List[PlacePredictionResponse])
async def search_google_places(client: HTTPClient, query: str = Query(min_length=2)):
    return await search_places(client, query)

@router.get("/places/{place_id}",
            summary='Get Place Details',
            response_model=BusinessPlaceDetailsResponse)
async def place_details(client: HTTPClient, place_id: str):
    return await get_place_details(client, place_id)

@router.get("/maps/static", summary="Proxy Google Static Maps")
async def static_map(
    http_client: HTTPClient,
    redis_client: RedisClient,
    center_lat: Optional[float] = None,
    center_lng: Optional[float] = None,
    address: Optional[str] = None,
    zoom: int = 15,
    width: int = 640,
    height: int = 360,
    scale: int = 2,
    maptype: str = "roadmap",
    language: str = "ro",
    region: Optional[str] = None,
    markers: List[str] = Query(default=[]),
    path: List[str] = Query(default=[]),
    style: List[str] = Query(default=[]),
    refresh: bool = False,
):
    query = StaticMapQuery(
        center_lat=center_lat,
        center_lng=center_lng,
        address=address,
        zoom=zoom,
        width=width,
        height=height,
        scale=scale,
        maptype=maptype,
        language=language,
        region=region,
        markers=markers,
        path=path,
        style=style,
        refresh=refresh,
    )
    return await fetch_static_map(http_client, redis_client, query)