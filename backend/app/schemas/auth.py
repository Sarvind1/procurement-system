from typing import Optional
from pydantic import BaseModel, EmailStr, constr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class UserRegister(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    full_name: str
    role: str = "user"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: constr(min_length=8) 