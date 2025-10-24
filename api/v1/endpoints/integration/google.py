from typing import List
from fastapi import APIRouter, Query

from core.dependencies import HTTPClient
from schema.integration.google import PlacePredictionResponse, BusinessPlaceDetailsResponse
from service.integration.google import search_places, get_place_details

router = APIRouter(prefix="/google", tags=["Google"])

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