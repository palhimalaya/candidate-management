from sqlalchemy import (
    JSON,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    REVIEWER = "reviewer"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    name = Column(
        String,
        nullable=False,
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password = Column(
        String,
        nullable=False,
    )

    role = Column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.REVIEWER,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    scores = relationship(
        "Score",
        back_populates="reviewer",
        cascade="all, delete-orphan",
    )


class CandidateStatus(str, enum.Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    HIRED = "hired"
    REJECTED = "rejected"


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True)

    name = Column(
        String,
        nullable=False,
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    role_applied = Column(
        String,
        nullable=False,
        index=True,
    )

    status = Column(
        Enum(CandidateStatus),
        nullable=False,
        default=CandidateStatus.NEW,
        index=True,
    )

    skills = Column(
        JSON,
        nullable=False,
        default=list,
    )

    internal_notes = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    deleted_at = Column(
        DateTime,
        nullable=True,
    )

    ai_summary = Column(
        Text,
        nullable=True,
    )

    scores = relationship(
        "Score",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True)

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    reviewer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    category = Column(
        String,
        nullable=False,
    )

    score = Column(
        Integer,
        nullable=False,
    )

    note = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    candidate = relationship(
        "Candidate",
        back_populates="scores",
    )

    reviewer = relationship(
        "User",
        back_populates="scores",
    )

    __table_args__ = (
        CheckConstraint(
            "score >= 1 AND score <= 5",
            name="check_score_range",
        ),
    )
