from datetime import datetime

from pydantic import BaseModel
from pydantic import EmailStr


class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class RegisterResponseSchema(BaseModel):
    message: str
    data: UserResponseSchema


class LoginDataSchema(BaseModel):
    access_token: str
    token_type: str
    user: UserResponseSchema


class LoginResponseSchema(BaseModel):
    message: str
    data: LoginDataSchema