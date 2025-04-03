import re
from typing import Optional, Any, Self

from pydantic import BaseModel, field_validator
from datetime import time

class ScheduleBase(BaseModel):
    day_of_week: str

class ScheduleCreate(ScheduleBase):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    time_offset: str

    @field_validator("time_offset")
    def validate(cls, value: Any) -> Self:
        if not re.match(r"^[+-]\d{2}:\d{2}:\d{2}$", value):
            raise ValueError("Time Offset must be in the format +-HH:MM:SS")

        sign, time_part = value[0], value[1:]
        hours, minutes, seconds = map(int, time_part.split(":"))

        if not(0 <= hours <= 23 and  0 <= minutes <= 59 and 0 <=seconds <= 59):
            raise ValueError("Invalid Offset Time Range")

        return value

class ScheduleUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    time_offset: str

    @field_validator("time_offset")
    def validate(cls, value: Any) -> Self:
        if not re.match(r"^[+-]\d{2}:\d{2}:\d{2}$", value):
            raise ValueError("Time Offset must be in the format +-HH:MM:SS")

        sign, time_part = value[0], value[1:]
        hours, minutes, seconds = map(int, time_part.split(":"))

        if not(0 <= hours <= 23 and  0 <= minutes <= 59 and 0 <=seconds <= 59):
            raise ValueError("Invalid Offset Time Range")

        return value

class ScheduleResponse(ScheduleBase):
    id: int
    user_id: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    time_offset: Optional[str] = None
    day_week_index: int

    class Config:
        from_attributes = True