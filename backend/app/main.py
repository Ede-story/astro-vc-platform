"""
StarMeet API - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="StarMeet API",
    description="Astrology calculation and profile API for StarMeet",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://star-meet.com",
        "http://localhost:3001",  # Local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker/Nginx"""
    return {"status": "healthy", "service": "starmeet-api"}


@app.get("/")
async def root():
    """API root - basic info"""
    return {
        "name": "StarMeet API",
        "version": "1.0.0",
        "docs": "/docs",
    }


# TODO: Import routers when ready
# from app.api import profiles, charts
# app.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
# app.include_router(charts.router, prefix="/charts", tags=["charts"])
