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
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
