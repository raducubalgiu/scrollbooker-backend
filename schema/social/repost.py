from pydantic import BaseModel, Field

class RepostCreate(BaseModel):
    comment: str = Field(max_length=300)