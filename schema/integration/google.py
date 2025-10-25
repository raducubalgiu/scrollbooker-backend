from typing import List, Optional

from pydantic import BaseModel, ConfigDict, conint, Field, field_validator


class PlacePredictionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    description: str
    place_id: str

class PlacesResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    predictions: List[PlacePredictionResponse]

class GoogleLocation(BaseModel):
    lat: float
    lng: float

class GoogleGeometry(BaseModel):
    location: GoogleLocation

class GoogleAddressComponent(BaseModel):
    long_name: str
    short_name: str
    types: List[str]

class GooglePlaceDetailsResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    place_id: Optional[str] = None
    formatted_address: str
    geometry: GoogleGeometry
    address_components: List[GoogleAddressComponent] = []

class GooglePlaceDetailsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    status: str
    result: Optional[GooglePlaceDetailsResult] = None
    error_message: Optional[str] = None

class BusinessPlaceDetailsResponse(BaseModel):
    place_id: str
    address: str
    lat: float
    lng: float
    country_code: Optional[str] = None
    city: Optional[str] = None
    route: Optional[str] = None
    street_number: Optional[str] = None
    postal_code: Optional[str] = None

class StaticMapQuery(BaseModel):
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    address: Optional[str] = None

    zoom: conint(ge=0, le=21) = 15
    width: conint(ge=1, le=640) = 640
    height: conint(ge=1, le=640) = 360
    scale: conint(ge=1, le=2) = 2
    maptype: str = Field(default="roadmap")
    language: str = Field(default="ro")
    region: Optional[str] = None

    #repeatable
    markers: List[str] = Field(default_factory=list)
    path: List[str] = Field(default_factory=list)
    style: List[str] = Field(default_factory=list)

    refresh: bool = False

