from pydantic import BaseModel, Field

class RolePermissionsBase(BaseModel):
    role_id: int
    permission_id: int

class RolePermissionsCreate(RolePermissionsBase):
    pass

class RolePermissionsResponse(RolePermissionsBase):
    id: int

    class Config:
        from_attributes = True