"""
Main FastAPI application for AI Code Review Tool
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional

from app.database import init_db
from app.routers import reviews, files, config, history, collaboration, audit, git
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    await init_db()
    yield

app = FastAPI(
    title="AI Code Review Tool",
    description="Comprehensive AI-powered code review API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(config.router, prefix="/api/v1/config", tags=["config"])
app.include_router(history.router, prefix="/api/v1/history", tags=["history"])
app.include_router(collaboration.router, prefix="/api/v1/collaboration", tags=["collaboration"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(git.router, prefix="/api/v1/git", tags=["git"])

@app.get("/")
async def root():
    return {"message": "AI Code Review Tool API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

