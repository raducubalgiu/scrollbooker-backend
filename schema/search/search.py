from typing import Literal, Optional

from pydantic import BaseModel

from schema.user.user import UserBaseMinimum

class SearchServiceBusinessTypeResponse(BaseModel):
    id: int
    name: str

class SearchResponse(BaseModel):
    type: Literal["keyword", "user", "service", "business_type"]
    label: str
    user: Optional[UserBaseMinimum] = None,
    service: Optional[SearchServiceBusinessTypeResponse] = None
    business_type: Optional[SearchServiceBusinessTypeResponse] = None