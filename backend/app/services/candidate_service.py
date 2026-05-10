from fastapi import HTTPException

from app.models import Candidate, CandidateStatus

from app.schemas import (
    CandidateCreateSchema,
    CandidateUpdateSchema,
)
from sqlalchemy.orm import Session
from sqlalchemy import or_, select
from datetime import datetime
from app.models import Score
import asyncio




def create_candidate(candidate_data: CandidateCreateSchema, db: Session):
    existing_candidate = (
        db.query(Candidate).filter(Candidate.email == candidate_data.email).first()
    )

    if existing_candidate:
        raise HTTPException(
            status_code=400,
            detail="Candidate with this email already exists",
        )

    new_candidate = Candidate(
        name=candidate_data.name,
        email=candidate_data.email,
        role_applied=candidate_data.role_applied,
        skills=candidate_data.skills,
        internal_notes=candidate_data.internal_notes,
    )

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return {"message": "Candidate created successfully", "data": new_candidate}


def list_candidates(
    page: int,
    page_size: int,
    status: CandidateStatus | None,
    role_applied: str | None,
    skill: str | None,
    keyword: str | None,
    db: Session,
):

    query = db.query(Candidate).filter(
        Candidate.deleted_at.is_(None),
    )

    if status:
        query = query.filter(Candidate.status == status)

    if role_applied:
        query = query.filter(Candidate.role_applied == role_applied)
    
    if skill:
        query = query.filter(Candidate.skills.contains(skill))

    if keyword:
        search = f"%{keyword}%"
        query = query.filter(
            or_(
                Candidate.name.ilike(search),
                Candidate.email.ilike(search),
            )
        )

    total = query.count()
    offset = (page - 1) * page_size

    candidates = (
        query.order_by(Candidate.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return {
        "message": "Candidates fetched successfully",
        "data": {
            "items": candidates,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


def update_candidate(
    db: Session, candidate_id: int, candidate_data: CandidateUpdateSchema
):

    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    for key, value in candidate_data.dict(exclude_unset=True).items():
        setattr(candidate, key, value)

    db.commit()
    db.refresh(candidate)

    return candidate


def delete_candidate(db: Session, candidate_id: int):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    candidate.status = CandidateStatus.REJECTED
    candidate.deleted_at = datetime.utcnow()
    db.commit()

    return candidate


def get_candidate_by_id(db: Session, candidate_id: int, user_id: int, is_admin: bool):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.deleted_at.is_(None))
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    query = select(Score).where(Score.candidate_id == candidate_id)
    if not is_admin:
        query = query.where(Score.reviewer_id == user_id)

    scores = db.execute(query.order_by(Score.created_at.desc())).scalars().all()

    response_data = {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "role_applied": candidate.role_applied,
        "status": candidate.status,
        "skills": candidate.skills,
        "internal_notes": candidate.internal_notes if is_admin else None,
        "ai_summary": getattr(candidate, "ai_summary", None),
        "created_at": candidate.created_at,
        "scores": [
            {
                "id": score.id,
                "category": score.category,
                "score": score.score,
                "note": score.note,
                "reviewer_id": score.reviewer_id,
                "reviewer_name": score.reviewer.name,
                "created_at": score.created_at,
            }
            for score in scores
        ],
    }

    return {"message": "Candidate fetched successfully", "data": response_data}


def create_score(db: Session, candidate_id: int, score_data, user_id: int):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.deleted_at.is_(None))
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    if not (1 <= score_data.score <= 5):
        raise HTTPException(
            status_code=400,
            detail="Score must be between 1 and 5",
        )

    new_score = Score(
        candidate_id=candidate_id,
        reviewer_id=user_id,
        category=score_data.category,
        score=score_data.score,
        note=score_data.note,
    )

    db.add(new_score)
    db.commit()
    db.refresh(new_score)

    return {
        "message": "Score submitted successfully",
        "data": {
            "id": new_score.id,
            "category": new_score.category,
            "score": new_score.score,
            "note": new_score.note,
            "reviewer_id": new_score.reviewer_id,
            "reviewer_name": new_score.reviewer.name,
            "created_at": new_score.created_at,
        },
    }


async def generate_ai_summary(db: Session, candidate_id: int):
    await asyncio.sleep(2)

    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.deleted_at.is_(None))
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    skills_str = ", ".join(candidate.skills) if candidate.skills else "none"

    summary = (
        f"AI Summary for {candidate.name}:\n"
        f"Candidate applied for {candidate.role_applied} position. "
        f"Key skills: {skills_str}. "
        f"Current status: {candidate.status.value}. "
        f"Based on the application, this candidate shows promising potential "
        f"in the relevant technical areas. Recommended for technical interview."
    )

    candidate.ai_summary = summary
    db.commit()

    return {
        "message": "AI summary generated successfully",
        "data": {
            "id": candidate.id,
            "ai_summary": summary,
        },
    }
