from pydantic import BaseModel, Field
from typing import Optional, List


class PermissionBase(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    code: str = Field(min_length=3, max_length=50)

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(PermissionBase):
    pass

class PermissionResponse(PermissionBase):
    id: int

    class Config:
        from_attributes = True

class RoleAssignment(BaseModel):
    id: int
    name: str
    assigned: bool

class PermissionWithRolesResponse(PermissionBase):
    id: int
    roles: List[RoleAssignment]


