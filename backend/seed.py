from datetime import datetime
import bcrypt
from app.database import engine, Base, SessionLocal
from app.models import User, Candidate, Score, UserRole, CandidateStatus
from sqlalchemy import select


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def seed_database():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        existing_users = session.execute(select(User).limit(1)).scalar_one_or_none()
        if existing_users:
            print("Database already seeded. Skipping...")
            return

        # Create users
        users_data = [
            {
                "name": "Admin User",
                "email": "admin@techkraft.com",
                "hashed_password": hash_password("admin123"),
                "role": UserRole.ADMIN,
            },
            {
                "name": "John Reviewer",
                "email": "john@techkraft.com",
                "hashed_password": hash_password("john123"),
                "role": UserRole.REVIEWER,
            },
            {
                "name": "Sarah Reviewer",
                "email": "sarah@techkraft.com",
                "hashed_password": hash_password("sarah123"),
                "role": UserRole.REVIEWER,
            },
        ]

        users = [User(**user_data) for user_data in users_data]
        session.add_all(users)
        session.flush()
        session.refresh(users[0])
        session.refresh(users[1])
        session.refresh(users[2])

        # Create candidates
        candidates_data = [
            {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "role_applied": "Frontend Developer",
                "status": CandidateStatus.NEW,
                "skills": ["React", "TypeScript", "CSS", "HTML", "Tailwind"],
                "internal_notes": "Strong portfolio, remote experience",
                "ai_summary": "Alice has 4 years of frontend experience with a focus on React. Strong skills in TypeScript and modern CSS frameworks. Previously worked on e-commerce platforms.",
            },
            {
                "name": "Bob Smith",
                "email": "bob@example.com",
                "role_applied": "Backend Developer",
                "status": CandidateStatus.REVIEWED,
                "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
                "internal_notes": "Good technical knowledge, needs behavioral interview",
                "ai_summary": "Bob has 3 years of backend development experience. Proficient in Python and FastAPI with strong database skills. Experience with microservices architecture.",
            },
            {
                "name": "Carol Davis",
                "email": "carol@example.com",
                "role_applied": "Full Stack Developer",
                "status": CandidateStatus.HIRED,
                "skills": ["JavaScript", "Node.js", "React", "MongoDB", "AWS"],
                "internal_notes": "Excellent problem solver, good culture fit",
                "ai_summary": "Carol is a senior full stack developer with 6 years of experience. Full stack proficiency with strong AWS skills. Led multiple successful projects.",
            },
            {
                "name": "David Wilson",
                "email": "david@example.com",
                "role_applied": "DevOps Engineer",
                "status": CandidateStatus.REJECTED,
                "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Terraform"],
                "internal_notes": "Insufficient experience with production environments",
                "ai_summary": "David has 2 years of DevOps experience. Strong theoretical knowledge but limited hands-on production experience. Would benefit from more practice.",
            },
            {
                "name": "Eva Martinez",
                "email": "eva@example.com",
                "role_applied": "Data Engineer",
                "status": CandidateStatus.NEW,
                "skills": ["Python", "SQL", "Spark", "Airflow", "dbt"],
                "internal_notes": "Referred by current employee",
                "ai_summary": "Eva has 4 years of data engineering experience. Strong SQL and Python skills. Experience with big data processing and pipeline orchestration.",
            },
        ]

        candidates = [Candidate(**candidate_data) for candidate_data in candidates_data]
        session.add_all(candidates)
        session.flush()
        session.refresh(candidates[0])
        session.refresh(candidates[1])
        session.refresh(candidates[2])
        session.refresh(candidates[3])
        session.refresh(candidates[4])

        # Create scores
        scores_data = [
            {
                "candidate_id": candidates[0].id,
                "reviewer_id": users[1].id,
                "category": "Technical Skills",
                "score": 4,
                "note": "Strong React knowledge, good TypeScript usage",
            },
            {
                "candidate_id": candidates[0].id,
                "reviewer_id": users[2].id,
                "category": "Communication",
                "score": 5,
                "note": "Clear and concise in responses",
            },
            {
                "candidate_id": candidates[1].id,
                "reviewer_id": users[0].id,
                "category": "Technical Skills",
                "score": 4,
                "note": "Good understanding of backend concepts",
            },
            {
                "candidate_id": candidates[1].id,
                "reviewer_id": users[1].id,
                "category": "Problem Solving",
                "score": 3,
                "note": "Took time to arrive at solutions",
            },
            {
                "candidate_id": candidates[1].id,
                "reviewer_id": users[2].id,
                "category": "System Design",
                "score": 4,
                "note": "Solid design patterns knowledge",
            },
            {
                "candidate_id": candidates[2].id,
                "reviewer_id": users[0].id,
                "category": "Technical Skills",
                "score": 5,
                "note": "Exceptional full stack knowledge",
            },
            {
                "candidate_id": candidates[2].id,
                "reviewer_id": users[1].id,
                "category": "Leadership",
                "score": 5,
                "note": "Great mentorship experience",
            },
            {
                "candidate_id": candidates[3].id,
                "reviewer_id": users[1].id,
                "category": "Technical Skills",
                "score": 3,
                "note": "Good basics but lacks production experience",
            },
            {
                "candidate_id": candidates[4].id,
                "reviewer_id": users[0].id,
                "category": "Technical Skills",
                "score": 4,
                "note": "Strong SQL and Python skills",
            },
        ]

        scores = [Score(**score_data) for score_data in scores_data]
        session.add_all(scores)

        session.commit()
        print("Database seeded successfully!")
        print(f"\nCreated {len(users)} users:")
        for user in users:
            print(f"  - {user.name} ({user.email}) - {user.role.value}")
        print(f"\nCreated {len(candidates)} candidates:")
        for candidate in candidates:
            print(f"  - {candidate.name} - {candidate.role_applied} - {candidate.status.value}")
        print(f"\nCreated {len(scores)} scores")


if __name__ == "__main__":
    seed_database()
