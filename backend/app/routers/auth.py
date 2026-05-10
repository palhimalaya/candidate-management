from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.dependencies import get_current_user

from app.schemas import (
    LoginResponseSchema,
    LoginSchema,
    RegisterSchema,
    RegisterResponseSchema,
    UserResponseSchema,
)
import app.services.auth_service as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponseSchema)
def register(
    payload: RegisterSchema,
    db: Session = Depends(get_db),
):
    return auth_service.register_user(payload, db)


@router.post("/login", response_model=LoginResponseSchema)
def login(
    payload: LoginSchema,
    db: Session = Depends(get_db),
):
    return auth_service.login_user(payload.email, payload.password, db)


@router.get("/me", response_model=UserResponseSchema)
def me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
