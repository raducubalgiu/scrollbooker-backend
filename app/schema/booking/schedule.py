from typing import Optional

from pydantic import BaseModel
from datetime import time

class ScheduleBase(BaseModel):
    day_of_week: str

class ScheduleCreate(ScheduleBase):
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class ScheduleUpdate(BaseModel):
    id: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class ScheduleResponse(ScheduleBase):
    id: int
    user_id: int
    business_id: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    day_week_index: int

    class Config:
        from_attributes = True