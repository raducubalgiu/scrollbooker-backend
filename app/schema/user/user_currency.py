from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class UserCurrencyBase(BaseModel):
    user_id: int
    currency_id: int

class UserCurrencyCreate(UserCurrencyBase):
    pass

class UserCurrencyUpdate(UserCurrencyBase):
    pass

class UserCurrencyResponse(UserCurrencyBase):
    id: int
    active: bool
    added_at: datetime
    removed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
