from fastapi import APIRouter

from app.api.v1.endpoints import proposals

api_router = APIRouter(prefix="/v1")
api_router.include_router(proposals.router)
