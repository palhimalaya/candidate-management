from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.models import User
from app.models import UserRole

from app.auth import (
    create_access_token,
    hash_password,
    verify_password,
)


def register_user(
    user_data,
    db: Session,
):
    existing_user = (
        db.query(User)
        .filter(
            User.email == user_data.email,
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists",
        )

    hashed_password = hash_password(
        user_data.password,
    )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=UserRole.REVIEWER,
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "data": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role.value,
            "created_at": new_user.created_at,
        },
    }


def login_user(
    email: str,
    password: str,
    db: Session,
):
    user = (
        db.query(User)
        .filter(
            User.email == email,
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password",
        )

    is_valid_password = verify_password(
        password,
        user.hashed_password,
    )

    if not is_valid_password:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role.value,
        }
    )

    return {
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.value,
                "created_at": user.created_at,
            },
        },
    }
