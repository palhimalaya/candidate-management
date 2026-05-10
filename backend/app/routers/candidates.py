from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from typing import Optional
from app.models import CandidateStatus, User, UserRole
from app.schemas import (
    CandidateCreateSchema,
    CandidateApiResponseSchema,
    CandidateListResponseSchema,
    CandidateResponseSchema,
    CandidateUpdateSchema,
    ScoreCreateSchema,
)
from app.services import candidate_service
from fastapi.responses import StreamingResponse
import json
from app.models import Score

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/", response_model=CandidateApiResponseSchema)
def create_candidate(
    candidate_data: CandidateCreateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return candidate_service.create_candidate(candidate_data, db)


@router.get("/", response_model=CandidateListResponseSchema)
def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    status: Optional[CandidateStatus] = None,
    role_applied: Optional[str] = None,
    skill: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return candidate_service.list_candidates(
        page=page,
        page_size=page_size,
        status=status,
        role_applied=role_applied,
        skill=skill,
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


@router.get("/{candidate_id}")
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_admin = current_user.role == UserRole.ADMIN
    return candidate_service.get_candidate_by_id(
        db, candidate_id, current_user.id, is_admin
    )


@router.post("/{candidate_id}/scores")
def create_score(
    candidate_id: int,
    score_data: ScoreCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return candidate_service.create_score(db, candidate_id, score_data, current_user.id)


@router.post("/{candidate_id}/summary")
async def generate_summary(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await candidate_service.generate_ai_summary(db, candidate_id)


@router.get("/{candidate_id}/stream")
async def stream_candidate_updates(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_admin = current_user.role == UserRole.ADMIN

    async def event_generator():
        query = db.query(Score).filter(Score.candidate_id == candidate_id)
        if not is_admin:
            query = query.filter(Score.reviewer_id == current_user.id)

        scores = query.order_by(Score.created_at.desc()).all()

        event_data = {
            "type": "scores_update",
            "data": [
                {
                    "id": score.id,
                    "category": score.category,
                    "score": score.score,
                    "note": score.note,
                    "reviewer_id": score.reviewer_id,
                    "reviewer_name": score.reviewer.name,
                    "created_at": score.created_at.isoformat(),
                }
                for score in scores
            ],
        }

        yield f"data: {json.dumps(event_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
