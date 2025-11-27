"""
StarMeet API - FastAPI Backend
Main application entry point

API Namespace: /star-api (via Nginx proxy)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.routers import astro


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle handler."""
    # Startup
    print("StarMeet API starting...")
    yield
    # Shutdown
    print("StarMeet API shutting down...")


app = FastAPI(
    title="StarMeet API",
    description="Vedic Astrology calculation and profile API for StarMeet",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path="/star-api",  # Important for Nginx proxy
    lifespan=lifespan,
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://star-meet.com",
        "http://localhost:3001",  # Local dev
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(astro.router, prefix="/v1", tags=["astro"])


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker/Nginx."""
    return {"status": "healthy", "service": "starmeet-api", "version": "1.0.0"}


@app.get("/")
async def root():
    """API root - basic info."""
    return {
        "name": "StarMeet API",
        "version": "1.0.0",
        "docs": "/star-api/docs",
        "endpoints": {
            "calculate": "POST /star-api/v1/calculate",
            "health": "GET /star-api/health",
        }
    }
