from typing import Optional

from pydantic import BaseModel
from datetime import time

class ScheduleBase(BaseModel):
    day_of_week: str

class ScheduleUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class ScheduleCreate(ScheduleBase):
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class ScheduleResponse(ScheduleBase):
    id: int
    user_id: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    class Config:
        from_attributes = True