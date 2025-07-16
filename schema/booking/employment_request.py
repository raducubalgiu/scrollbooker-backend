from pydantic import BaseModel

from core.enums.employment_requests_status_enum import EmploymentRequestsStatusEnum
from schema.nomenclature.profession import ProfessionResponse
from schema.user.user import UserBaseMinimum

class EmploymentRequestCreate(BaseModel):
    consent_id: int
    employee_id: int
    profession_id: int

class EmploymentRequestUpdate(BaseModel):
    status: EmploymentRequestsStatusEnum

class EmploymentsRequestsResponse(BaseModel):
    id: int
    status: EmploymentRequestsStatusEnum
    employee: UserBaseMinimum
    employer: UserBaseMinimum
    profession: ProfessionResponse

    class Config:
        from_attributes = True
