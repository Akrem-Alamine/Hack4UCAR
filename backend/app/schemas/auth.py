from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: UserRole
    institution_id: Optional[int]
    domain_scope: Optional[str] = None

    model_config = {"from_attributes": True}


TokenResponse.model_rebuild()
