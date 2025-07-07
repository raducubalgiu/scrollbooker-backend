from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class ConsentBase(BaseModel):
    name: str = Field(min_length=3, max_length=50),
    title: str = Field(min_length=3, max_length=100)
    text: str

class ConsentCreate(ConsentBase):
    version: Optional[str] = None

class ConsentUpdate(ConsentBase):
    version: Optional[str] = None

class ConsentResponse(ConsentBase):
    id: int
    version: str
    created_at: datetime