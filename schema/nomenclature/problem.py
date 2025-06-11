from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime

class ProblemBase(BaseModel):
    text: str = Field(min_length=20, max_length=500)
    user_id: int

class ProblemCreate(ProblemBase):
    pass

class ProblemResponse(ProblemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None