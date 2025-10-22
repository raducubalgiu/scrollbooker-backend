from typing import Optional

from pydantic import BaseModel
from datetime import datetime
from core.enums.employment_requests_status_enum import EmploymentRequestsStatusEnum
from schema.nomenclature.profession import ProfessionResponse

class EmploymentRequestCreate(BaseModel):
    consent_id: int
    employee_id: int
    profession_id: int

class EmploymentRequestUpdate(BaseModel):
    status: EmploymentRequestsStatusEnum

class EmploymentRequestUser(BaseModel):
    id: int
    fullname: str
    username: str
    avatar: Optional[str] = None
    profession: str

class EmploymentsRequestsResponse(BaseModel):
    id: int
    created_at: datetime
    status: EmploymentRequestsStatusEnum
    employee: EmploymentRequestUser
    employer: EmploymentRequestUser
    profession: ProfessionResponse

    class Config:
        from_attributes = True
