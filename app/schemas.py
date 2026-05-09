from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from pydantic import EmailStr
from app.models import CandidateStatus


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


class CandidateCreateSchema(BaseModel):
    name: str
    email: EmailStr
    role_applied: str
    skills: List[str]
    internal_notes: Optional[str] = None


class CandidateUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role_applied: Optional[str] = None
    status: Optional[CandidateStatus] = None
    skills: Optional[List[str]] = None
    internal_notes: Optional[str] = None


class CandidateResponseSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_applied: str
    status: CandidateStatus
    skills: List[str]
    internal_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateApiResponseSchema(BaseModel):
    message: str
    data: CandidateResponseSchema


class CandidateListDataSchema(BaseModel):
    items: list[CandidateResponseSchema]
    total: int
    page: int
    page_size: int


class CandidateListResponseSchema(BaseModel):
    message: str
    data: CandidateListDataSchema
