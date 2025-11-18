from typing import TypedDict
from datetime import datetime
from pydantic import BaseModel, EmailStr

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshToken(BaseModel):
    refresh_token: str

class TokenPayload(BaseModel):
    id: int
    username: str
    fullname: str
    email: EmailStr
    role: str

class EncodedTokenClaims(TypedDict):
    id: int
    sub: str
    fullname: str
    email: str
    role: str
    exp: datetime