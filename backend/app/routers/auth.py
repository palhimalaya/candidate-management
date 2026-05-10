from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

from app.schemas import LoginResponseSchema, LoginSchema, RegisterSchema, RegisterResponseSchema
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
