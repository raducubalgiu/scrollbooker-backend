from pydantic import BaseModel, Field

from core.enums.role_enum import RoleEnum

class RoleBase(BaseModel):
    name: RoleEnum = Field(min_length=3, max_length=50)

    class Config:
        from_attributes = True

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int
    active: bool

    class Config:
        from_attributes = True