from pydantic import EmailStr, Field
from app.schemas.base import BaseSchema

class UserRegister(BaseSchema):
    email: str = Field(..., description="Email address of the user")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")

class UserLogin(BaseSchema):
    email: str = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password")

class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseSchema):
    refresh_token: str

class UserResponse(BaseSchema):
    id: int
    email: str
    is_active: bool
