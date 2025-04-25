from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class EmploymentRequestBase(BaseModel):
    employee_id: int

    class Config:
        from_attributes = True

class EmploymentRequestUpdate(BaseModel):
    status: str

class EmploymentRequestCreate(EmploymentRequestBase):
    pass

class EmploymentRequestResponse(EmploymentRequestBase):
    id: int
    employer_id: int
    business_id: int
    employee_username: str
    employer_username: str
    status: str
    created_at: datetime
    ended_by: Optional[int] = None
    ended_by_username: Optional[str] = None
    start_date: Optional[datetime] = None

    class Config:
        from_attributes = True
