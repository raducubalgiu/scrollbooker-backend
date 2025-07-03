import httpx
import os

from starlette import status
from starlette.exceptions import HTTPException

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
BASE_URL = os.getenv("GOOGLE_PLACES_BASE_URL")

async def search_places(query: str):
    url = f"{BASE_URL}/autocomplete/json"
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

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    data = response.json()

    results = [
        {
            "description": item["description"],
            "place_id": item["place_id"]
        }
        for item in data.get("predictions", [])
    ]
    return results

async def get_place_details(place_id: str):
    url = f"{BASE_URL}/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_address,geometry,address_components",
        "key": API_KEY,
        "language": "ro"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

        data = response.json()

        if data["status"] != "OK":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Something went wrong"
            )

        result = data.get("result", {})
        location = result.get("geometry", {}).get("location", {})

        return {
            "place_id": place_id,
            "address": result.get("formatted_address"),
            "lat": location.get("lat"),
            "lng": location.get("lng")
        }

