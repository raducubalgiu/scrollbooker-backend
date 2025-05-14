from typing import Optional

from pydantic import BaseModel, constr
from datetime import datetime

class HashtagCreate(BaseModel):
    name: constr(min_length=2, max_length=50, pattern=r"^\w+$") #Only letters/numbers - no #

    @classmethod
    def validate_name(cls, value: str) -> str:
        return value.lower()

class HashtagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
