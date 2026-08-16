from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="Amiri - Automated B2B Commercial Proposal Generator API",
    version="1.0.0",
    description="Backend REST API for multi-agent commercial proposal generation.",
)

# Configure CORS
origins = [origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root-level health check endpoint
app.include_router(health_router)

# Versioned API routes
app.include_router(api_router, prefix="/api")
