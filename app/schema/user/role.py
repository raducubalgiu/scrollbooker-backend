from pydantic import BaseModel, Field

class RoleBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    active: bool

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True