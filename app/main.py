from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.candidates import router as candidates_router

app = FastAPI(
    title="TechKraft API",
    version="1.0.0",
)


@app.get("/")
def health_check():
    return {
        "message": "API is running",
    }


app.include_router(auth_router)
app.include_router(candidates_router)
