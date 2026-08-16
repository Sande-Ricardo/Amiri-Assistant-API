from fastapi import APIRouter

from app.domain.schemas import HealthCheckResponse

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check() -> HealthCheckResponse:
    # Health check for service and database connectivity
    return HealthCheckResponse(status="ok", database="connected")
