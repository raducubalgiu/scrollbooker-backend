from typing import Optional
from pydantic import BaseModel, HttpUrl

class PostMediaResponse(BaseModel):
    id: int
    url: HttpUrl
    type: str
    thumbnail_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True