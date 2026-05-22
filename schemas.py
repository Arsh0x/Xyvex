from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ProjectCreate(BaseModel):
    name: str
    target: str

class FindingCreate(BaseModel):
    title: str
    severity: str
    notes: Optional[str] = None

class PayloadCreate(BaseModel):
    name: str
    content: str
    category: str