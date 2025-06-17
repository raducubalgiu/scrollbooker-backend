from typing import Optional
from pydantic import BaseModel, HttpUrl

class PostMediaResponse(BaseModel):
    id: int
    url: HttpUrl
    type: str
    thumbnail_url: str = None
    order_index: int
    duration: Optional[float] = None

    class Config:
        from_attributes = True