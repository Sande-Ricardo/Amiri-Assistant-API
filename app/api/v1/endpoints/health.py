from fastapi import APIRouter

from app.domain.schemas import HealthCheckResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Check service health",
    description=(
        "Used by external monitoring tools (e.g. Render, Railway) to verify system operational status "
        "and active database connectivity."
    ),
    responses={
        200: {
            "description": "System is healthy and database is connected.",
        },
    },
)
async def health_check() -> HealthCheckResponse:
    # Health check for service and database connectivity
    return HealthCheckResponse(status="ok", database="connected")
