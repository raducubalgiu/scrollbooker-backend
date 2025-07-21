from typing import Optional
from pydantic import BaseModel

from core.enums.registration_step_enum import RegistrationStepEnum

class OnBoardingResponse(BaseModel):
    is_validated: bool
    registration_step: Optional[RegistrationStepEnum] = None