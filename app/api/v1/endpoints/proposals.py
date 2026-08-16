from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.adapters.database.mysql import InMemoryProposalRepository
from app.domain.schemas import (
    ProposalCreateRequest,
    ProposalCreateResponse,
    ProposalStatusResponse,
)
from app.services.proposals import ProposalService

router = APIRouter(prefix="/proposals", tags=["Proposals"])

# Temporary dependency until DB injection is configured
repository = InMemoryProposalRepository()
proposal_service = ProposalService(repository)


@router.post(
    "/generate",
    response_model=ProposalCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Initiate commercial proposal generation",
    description=(
        "Receives unstructured commercial requirements from a client, initializes a pending proposal request, "
        "and triggers the asynchronous multi-agent orchestration pipeline (Analyst -> Architect -> Writer) "
        "in the background via BackgroundTasks."
    ),
    responses={
        202: {
            "description": "Request accepted and queued for asynchronous processing.",
        },
        422: {
            "description": "Validation Error (e.g. raw_requirements text too short or empty).",
        },
        500: {
            "description": "Internal server error while initializing the request.",
        },
    },
)
async def generate_proposal(
    payload: ProposalCreateRequest,
    background_tasks: BackgroundTasks,
) -> ProposalCreateResponse:
    request_id = await proposal_service.initiate_generation(
        raw_requirements=payload.raw_requirements,
        client_name=payload.client_name,
        background_tasks=background_tasks,
    )

    return ProposalCreateResponse(
        request_id=request_id,
        status="pending",
        status_check_url=f"/api/v1/proposals/{request_id}/status",
        created_at=datetime.now(timezone.utc),
    )


@router.get(
    "/{request_id}/status",
    response_model=ProposalStatusResponse,
    summary="Poll proposal generation status",
    description=(
        "Retrieves the current execution status and granular pipeline stage for a given request. "
        "When the pipeline reaches status 'completed', the response contains the final commercial proposal "
        "in Markdown format along with structured metadata."
    ),
    responses={
        200: {
            "description": "Status payload retrieved successfully.",
        },
        404: {
            "description": "No proposal request found with the specified UUID.",
        },
    },
)
async def get_proposal_status(request_id: UUID) -> ProposalStatusResponse:
    request_data = await proposal_service.check_status(request_id)
    if not request_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal request with ID '{request_id}' was not found.",
        )

    return ProposalStatusResponse(**request_data)
