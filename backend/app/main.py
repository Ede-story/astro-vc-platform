"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Astro-VC Backend...")
    logger.info("📊 Loading AI models...")
    # TODO: Load VedAstro engine
    # TODO: Load AstroSage-LLaMA model
    # TODO: Initialize OpenSearch connection
    logger.info("✅ Application started successfully")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Astro-VC Backend...")
    # TODO: Cleanup resources
    logger.info("✅ Shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="Astro-VC API",
    description="AI-powered VC matching platform using Vedic astrology and LLM",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Welcome to Astro-VC API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    from app.services.vedastro_engine import VEDASTRO_AVAILABLE, get_vedastro_engine

    vedastro_ready = VEDASTRO_AVAILABLE
    redis_ready = False

    if vedastro_ready:
        try:
            engine = get_vedastro_engine()
            redis_ready = engine.redis_available
        except:
            pass

    return {
        "status": "healthy",
        "version": "0.1.0",
        "vedastro_ready": vedastro_ready,
        "redis_ready": redis_ready,
        "llm_ready": False  # TODO: Check AstroSage-LLaMA
    }


# Import routers
from app.api.routes import rating_router

# Include routers
app.include_router(rating_router)

# TODO: Add more routers when implemented
# from app.api.routes import rectification, matching
# app.include_router(rectification.router, prefix="/api/v1", tags=["rectification"])
# app.include_router(matching.router, prefix="/api/v1", tags=["matching"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Development only
    )
