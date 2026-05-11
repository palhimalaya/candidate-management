# Candidate Dashboard

A full-stack web application for managing candidate assessments with role-based access control, AI-generated summaries, and real-time scoring capabilities.

## Tech Stack

### Backend

- **FastAPI** - Modern Python web framework with async support
- **SQLite** - Lightweight database for this deployment
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and serialization
- **python-jose** - JWT token generation and validation
- **bcrypt** - Password hashing

### Frontend

- **React 19** - UI library
- **Vite** - Build tool and dev server
- **TypeScript** - Type safety
- **React Router** - Client-side routing
- **Axios** - HTTP client

### DevOps

- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## Setup and Run Instructions

### Using Docker Compose (Recommended)

1. **Clone the repository and navigate to the project root**

```bash
git clone <repository-url>
cd project
```

2. **Create environment file**

```bash
cp .env.example .env
```

3. **Start the services**

```bash
docker-compose up --build
```

4. **Run Seed file for dummy data**

```bash
docker-compose exec backend python seed.py
```

5. **Access the application**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

**To use below Crediantial run seed:**
- Admin Cred: 
    ```
    email: admin@techkraft.com
    password: admin123
    ```
- Reviewer Cred: 
    ```
    email: john@techkraft.com
    password: john123
    ```

### Running Locally (Development)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Initialize database
alembic upgrade head

# Run the server
uvicorn app.main:app --reload

# Run the seed
python seed.py
```



The backend will start on port 8000.

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

The frontend will start on port 5173.

## Testing

Run the backend test suite:

```bash
cd backend
pytest tests/ -v
```

Tests cover:

- API endpoint functionality
- Authentication and authorization enforcement
- Role-based data filtering
- Pagination and filtering
- Soft delete behavior

## Architecture Decision Records (ADR)

### ADR-001: FastAPI over Other Frameworks

**Context:**
We needed a Python web framework for building a REST API with async support, automatic documentation, and type safety.

**Decision:**
Chose FastAPI over Flask and Django REST Framework.

The choice enables rapid development with clear API contracts and aligns with modern Python async patterns.

### ADR-002: SQLite with Soft Deletes over Hard Deletes

**Context:**
The system needs to handle candidate deletions while preserving data for audit purposes and potential recovery.

**Decision:**
Implemented soft deletes using a `deleted_at` timestamp column in the database.

**Trade-offs:**

- **Pros:** Data preservation for audits, ability to restore deleted candidates, simpler recovery workflow, compliance with retention policies
- **Cons:** Requires filtering `deleted_at` in all queries, slightly increased query complexity, storage overhead

Soft deletes provide critical audit trail capabilities for a recruitment system where data history matters.

### ADR-003: JWT with Role Hardcoded at Registration

**Context:**
The system requires role-based access control with two roles: reviewer and admin.

**Decision:**
JWT-based authentication with roles hardcoded to "reviewer" at registration. Admin users must be manually added to the database.

**Trade-offs:**

- **Pros:** Prevents role escalation attacks, simplifies registration flow, reduces attack surface
- **Cons:** Admin onboarding requires manual database intervention, no user management in this project.

This security-first approach prioritizes preventing unauthorized access over convenience for admin account creation.

# Debugging Signal — Query Pattern Analysis

## Problematic Code

```python
def search_candidates(status: str, keyword: str, page: int, page_size: int):
    all_candidates = db.execute("SELECT * FROM candidates").fetchall()

    filtered = [
        c for c in all_candidates
        if c["status"] == status
    ]

    offset = (page - 1) * page_size

    return filtered[offset : offset + page_size]
```

---

## Issues

### 1. Fetch-Then-Filter Anti-Pattern

The query loads the entire `candidates` table into application memory before filtering.

This causes:

- high memory usage
- unnecessary network transfer
- slower response times

---

### 2. No Index Utilization

Filtering happens in Python instead of SQL:

```python
[c for c in all_candidates if c["status"] == status]
```

As a result, database indexes cannot be used efficiently.

---

### 3. Inefficient Pagination

Pagination is applied after loading all rows:

```python
filtered[offset : offset + page_size]
```

This means page 1 and page 1000 both require processing the full dataset.

---

### 4. Missing Stable Ordering

The query lacks `ORDER BY`, which can cause inconsistent pagination results.

---

## Correct Approach

Filtering, searching, sorting, and pagination should be handled by the database.

```python
def search_candidates(status: str, keyword: str, page: int, page_size: int):
    offset = (page - 1) * page_size

    query = """
        SELECT id, name, email, status, created_at
        FROM candidates
        WHERE status = :status
          AND name ILIKE :keyword
        ORDER BY created_at DESC
        LIMIT :limit
        OFFSET :offset
    """

    params = {
        "status": status,
        "keyword": f"%{keyword}%",
        "limit": page_size,
        "offset": offset,
    }

    return db.execute(query, params).fetchall()
```

---

## Why This Is Better

- Uses database indexes efficiently
- Reduces memory and network usage
- Returns only required rows
- Provides stable pagination
- Scales much better for large datasets

## Learning Reflection

**What I tried for the first time:**

Implementing Server-Sent Events (SSE) for real-time score updates was a new experience. While the assignment listed it as a stretch goal, I wanted to explore how to handle streaming responses in FastAPI. The implementation taught me about async generators and the StreamingResponse class, and how to manage database sessions in an async streaming context.

**What I would explore given more time:**

I'd investigate integrating a real LLM API (like OpenAI or Anthropic) for the AI summary generation feature. The current mock with a 2-second sleep is functional but doesn't provide actual value. I'd also implement proper error handling for streaming connections and explore WebSocket as an alternative for bi-directional real-time updates.

## Known Limitations

1. **Admin Account Creation**: Admin users must be manually inserted into the database or use seed file as registration only creates reviewer accounts.

2. **AI Summary**: Currently mocked with a 2-second delay. Real LLM integration would require API keys and additional error handling.

3. **SSE Endpoint**: While implemented, the frontend doesn't consume it. Integration would require EventSource handling and connection management.

4. **Database**: SQLite is used for simplicity. Production deployments should consider PostgreSQL or other production-grade databases.
