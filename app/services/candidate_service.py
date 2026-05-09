from fastapi import HTTPException

from app.models import Candidate, CandidateStatus

from app.schemas import (
    CandidateCreateSchema,
    CandidateUpdateSchema,
)
from sqlalchemy.orm import Session
from sqlalchemy import or_


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

    # Update the candidate's attributes
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

    db.delete(candidate)
    db.commit()

    return candidate
