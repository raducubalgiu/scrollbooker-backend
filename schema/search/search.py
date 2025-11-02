from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel
from datetime import datetime

class SearchServiceBusinessTypeResponse(BaseModel):
    id: int
    name: str

class SearchUserResponse(BaseModel):
    id: int
    fullname: Optional[str] = None
    username: str = None
    profession: Optional[str] = None
    avatar: Optional[str] = None
    ratings_average: Optional[Decimal] = None
    distance: Optional[float] = None
    is_business_or_employee: Optional[bool] = False

class SearchResponse(BaseModel):
    type: Literal["keyword", "user", "service", "business_type"]
    label: str
    user: Optional[SearchUserResponse] = None,
    service: Optional[SearchServiceBusinessTypeResponse] = None
    business_type: Optional[SearchServiceBusinessTypeResponse] = None

class UserSearchHistoryResponse(BaseModel):
    id: int
    keyword: str
    created_at: datetime

class SearchCreate(BaseModel):
    keyword: str