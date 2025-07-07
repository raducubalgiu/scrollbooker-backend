from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from core.enums.employment_requests_status_enum import EmploymentRequestsStatusEnum
from schema.user.user import UserBaseMinimum

class EmploymentRequestBase(BaseModel):
    employee_id: int
    profession_id: int

class EmploymentRequestCreate(EmploymentRequestBase):
    consent_id: int

class EmploymentRequestUpdate(BaseModel):
    status: EmploymentRequestsStatusEnum

class ProfessionLoadOnly(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class EmploymentRequestResponse(EmploymentRequestBase):
    id: int
    profession_id: Optional[int] = None
    employer_id: int
    business_id: int
    status: str
    created_at: datetime
    ended_by: Optional[int] = None
    start_date: Optional[datetime] = None
    employee: UserBaseMinimum
    employer: UserBaseMinimum
    profession: Optional[ProfessionLoadOnly] = None

    class Config:
        from_attributes = True
