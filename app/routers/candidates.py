from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from typing import Optional
from app.models import CandidateStatus, User
from app.schemas import (
    CandidateCreateSchema,
    CandidateListResponseSchema,
    CandidateResponseSchema,
    CandidateUpdateSchema,
)
from app.services import candidate_service

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/", response_model=CandidateResponseSchema)
def create_candidate(
    candidate_data: CandidateCreateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return candidate_service.create_candidate(db, candidate_data)


@router.get("/", response_model=CandidateListResponseSchema)
def list_candidates(
    page: int = 1,
    page_size: int = 10,
    status: Optional[CandidateStatus] = None,
    role_applied: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return candidate_service.list_candidates(
        page=page,
        page_size=page_size,
        status=status,
        role_applied=role_applied,
        keyword=keyword,
        db=db,
    )


@router.put("/{candidate_id}", response_model=CandidateResponseSchema)
def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return candidate_service.update_candidate(db, candidate_id, candidate_data)


@router.delete("/{candidate_id}")
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return candidate_service.delete_candidate(db, candidate_id)
