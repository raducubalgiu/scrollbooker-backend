from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class CurrencyBase(BaseModel):
    name: str = Field(min_length=3, max_length=3)

class CurrencyCreate(CurrencyBase):
    pass

class CurrencyUpdate(CurrencyBase):
    active: bool

class CurrencyResponse(CurrencyBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CurrencyMiniResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserCurrenciesUpdate(BaseModel):
    currency_ids: List[int]