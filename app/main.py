from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import engine, Base
from app.routers import teams, users
from app.models import Team, User

app = FastAPI(
    title="PR Reviewer Assignment Service",
    version="1.0.0",
    description="Сервис назначения ревьюеров для Pull Request'ов"
)

app.include_router(teams.router)
app.include_router(users.router)


@app.on_event("startup")
async def startup_event():
    pass


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Database error occurred"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "PR Reviewer Assignment Service",
        "version": "1.0.0"
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "PR Reviewer Assignment Service",
        "docs": "/docs",
        "health": "/health"
    }

