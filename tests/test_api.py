import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app.models import Base, User, Candidate, Score, UserRole
from app.auth import hash_password
import asyncio



@pytest.fixture
def client():
    from app.database import engine

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = Session(bind=engine)
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db(client):
    from app.database import Session
    return Session(bind=app.dependency_overrides[get_db]().__enter__())


@pytest.fixture
def admin_user(test_db):
    user = User(
        name="Admin User",
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        role=UserRole.ADMIN,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def reviewer_user(test_db):
    user = User(
        name="Reviewer User",
        email="reviewer@test.com",
        hashed_password=hash_password("reviewer123"),
        role=UserRole.REVIEWER,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def other_reviewer_user(test_db):
    user = User(
        name="Other Reviewer",
        email="other@test.com",
        hashed_password=hash_password("other123"),
        role=UserRole.REVIEWER,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post(
        "/auth/login",
        json={"email": "admin@test.com", "password": "admin123"},
    )
    return response.json()["data"]["access_token"]


@pytest.fixture
def reviewer_token(client, reviewer_user):
    response = client.post(
        "/auth/login",
        json={"email": "reviewer@test.com", "password": "reviewer123"},
    )
    return response.json()["data"]["access_token"]


@pytest.fixture
def other_reviewer_token(client, other_reviewer_user):
    response = client.post(
        "/auth/login",
        json={"email": "other@test.com", "password": "other123"},
    )
    return response.json()["data"]["access_token"]


def test_create_candidate_verify_response(client, admin_token):
    response = client.post(
        "/candidates/",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "role_applied": "Software Engineer",
            "skills": ["Python", "FastAPI"],
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Candidate created successfully"

    candidate_data = data["data"]
    assert candidate_data["name"] == "John Doe"
    assert candidate_data["email"] == "john@example.com"
    assert candidate_data["role_applied"] == "Software Engineer"
    assert candidate_data["skills"] == ["Python", "FastAPI"]
    assert candidate_data["status"] == "new"
    assert "id" in candidate_data
    assert "created_at" in candidate_data


def test_candidate_filters_and_pagination(client, admin_token, test_db):
    for i in range(25):
        candidate = Candidate(
            name=f"Candidate {i}",
            email=f"candidate{i}@example.com",
            role_applied="Software Engineer" if i % 2 == 0 else "Frontend Developer",
            skills=["Python"] if i % 2 == 0 else ["JavaScript"],
        )
        test_db.add(candidate)
    test_db.commit()

    response = client.get(
        "/candidates/?page=1&page_size=10&status=new&role_applied=Software Engineer",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["page"] == 1
    assert data["data"]["page_size"] == 10
    assert len(data["data"]["items"]) == 10
    assert data["data"]["total"] == 13


def test_create_score(client, reviewer_token, test_db):
    candidate = Candidate(
        name="Test Candidate",
        email="test@example.com",
        role_applied="Software Engineer",
        skills=["Python"],
    )
    test_db.add(candidate)
    test_db.commit()

    response = client.post(
        f"/candidates/{candidate.id}/scores",
        json={
            "category": "Technical Skills",
            "score": 4,
            "note": "Strong Python knowledge",
        },
        headers={"Authorization": f"Bearer {reviewer_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Score submitted successfully"
    assert data["data"]["category"] == "Technical Skills"
    assert data["data"]["score"] == 4


def test_auth_enforcement_reviewer_cannot_see_other_scores(client, reviewer_token, other_reviewer_token, test_db):
    candidate = Candidate(
        name="Test Candidate",
        email="test@example.com",
        role_applied="Software Engineer",
        skills=["Python"],
    )
    test_db.add(candidate)
    test_db.commit()

    client.post(
        f"/candidates/{candidate.id}/scores",
        json={
            "category": "Technical Skills",
            "score": 5,
            "note": "Excellent",
        },
        headers={"Authorization": f"Bearer {reviewer_token}"},
    )

    client.post(
        f"/candidates/{candidate.id}/scores",
        json={
            "category": "Communication",
            "score": 3,
            "note": "Needs improvement",
        },
        headers={"Authorization": f"Bearer {other_reviewer_token}"},
    )

    response = client.get(
        f"/candidates/{candidate.id}",
        headers={"Authorization": f"Bearer {reviewer_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    scores = data["data"]["scores"]

    assert len(scores) == 1
    assert scores[0]["category"] == "Technical Skills"
    assert scores[0]["score"] == 5


def test_admin_can_see_all_scores(client, admin_token, reviewer_token, other_reviewer_token, test_db):
    candidate = Candidate(
        name="Test Candidate",
        email="test@example.com",
        role_applied="Software Engineer",
        skills=["Python"],
    )
    test_db.add(candidate)
    test_db.commit()

    client.post(
        f"/candidates/{candidate.id}/scores",
        json={
            "category": "Technical Skills",
            "score": 5,
        },
        headers={"Authorization": f"Bearer {reviewer_token}"},
    )

    client.post(
        f"/candidates/{candidate.id}/scores",
        json={
            "category": "Communication",
            "score": 3,
        },
        headers={"Authorization": f"Bearer {other_reviewer_token}"},
    )

    response = client.get(
        f"/candidates/{candidate.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    scores = data["data"]["scores"]

    assert len(scores) == 2


def test_reviewer_cannot_see_internal_notes(client, reviewer_token, admin_token, test_db):
    candidate = Candidate(
        name="Test Candidate",
        email="test@example.com",
        role_applied="Software Engineer",
        skills=["Python"],
        internal_notes="Internal admin notes",
    )
    test_db.add(candidate)
    test_db.commit()

    response = client.get(
        f"/candidates/{candidate.id}",
        headers={"Authorization": f"Bearer {reviewer_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["internal_notes"] is None

    response = client.get(
        f"/candidates/{candidate.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["internal_notes"] == "Internal admin notes"


def test_soft_delete_not_hard_delete(client, admin_token, test_db):
    candidate = Candidate(
        name="Test Candidate",
        email="test@example.com",
        role_applied="Software Engineer",
        skills=["Python"],
    )
    test_db.add(candidate)
    test_db.commit()

    candidate_id = candidate.id

    response = client.delete(
        f"/candidates/{candidate_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200

    from app.database import Session
    db = Session(bind=app.dependency_overrides[get_db]().__enter__())
    deleted_candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    assert deleted_candidate is not None
    assert deleted_candidate.deleted_at is not None
    assert deleted_candidate.status.value == "rejected"


def test_ai_summary_generation(client, reviewer_token, test_db):
    candidate = Candidate(
        name="Test Candidate",
        email="test@example.com",
        role_applied="Software Engineer",
        skills=["Python", "FastAPI"],
    )
    test_db.add(candidate)
    test_db.commit()

    async def test_async():
        response = client.post(
            f"/candidates/{candidate.id}/summary",
            headers={"Authorization": f"Bearer {reviewer_token}"},
        )
        return response

    response = asyncio.run(test_async())

    assert response.status_code == 200
    data = response.json()
    assert "ai_summary" in data["data"]
    assert "AI Summary" in data["data"]["ai_summary"]


def test_keyword_search(client, admin_token, test_db):
    candidate1 = Candidate(
        name="Alice Johnson",
        email="alice@example.com",
        role_applied="Software Engineer",
        skills=["Python"],
    )
    candidate2 = Candidate(
        name="Bob Smith",
        email="bob@example.com",
        role_applied="Frontend Developer",
        skills=["JavaScript"],
    )
    test_db.add_all([candidate1, candidate2])
    test_db.commit()

    response = client.get(
        "/candidates/?keyword=Alice",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]["items"]) == 1
    assert data["data"]["items"][0]["name"] == "Alice Johnson"


def test_skill_filter(client, admin_token, test_db):
    candidate1 = Candidate(
        name="Python Dev",
        email="python@example.com",
        role_applied="Software Engineer",
        skills=["Python", "FastAPI"],
    )
    candidate2 = Candidate(
        name="JS Dev",
        email="js@example.com",
        role_applied="Frontend Developer",
        skills=["JavaScript", "React"],
    )
    test_db.add_all([candidate1, candidate2])
    test_db.commit()

    response = client.get(
        "/candidates/?skill=Python",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]["items"]) == 1
    assert data["data"]["items"][0]["skills"] == ["Python", "FastAPI"]


def test_score_validation(client, reviewer_token, test_db):
    candidate = Candidate(
        name="Test Candidate",
        email="test@example.com",
        role_applied="Software Engineer",
        skills=["Python"],
    )
    test_db.add(candidate)
    test_db.commit()

    response = client.post(
        f"/candidates/{candidate.id}/scores",
        json={
            "category": "Technical Skills",
            "score": 6,
        },
        headers={"Authorization": f"Bearer {reviewer_token}"},
    )

    assert response.status_code == 400
