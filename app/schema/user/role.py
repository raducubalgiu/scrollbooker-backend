from pydantic import BaseModel, Field

class RoleBase(BaseModel):
    name: str = Field(min_length=3, max_length=50)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int
    active: bool

    class Config:
        from_attributes = True