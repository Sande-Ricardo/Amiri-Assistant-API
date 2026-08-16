from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ProposalCreateRequest(BaseModel):
    raw_requirements: str = Field(
        ...,
        min_length=20,
        description="Free text containing raw client requirements.",
    )
    client_name: str | None = Field(
        default=None,
        description="Optional client or company name.",
    )


class ProposalCreateResponse(BaseModel):
    request_id: UUID
    status: Literal["pending", "processing", "completed", "failed"]
    status_check_url: str
    created_at: datetime


class ProposalData(BaseModel):
    final_markdown: str
    total_estimated_hours: int
    suggested_tech_stack: dict[str, Any]
    identified_ambiguities: list[str]
    resolved_assumptions: list[str]


class ProposalStatusResponse(BaseModel):
    request_id: UUID
    status: Literal["pending", "processing", "completed", "failed"]
    current_node: str | None = None
    proposal: ProposalData | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class HealthCheckResponse(BaseModel):
    status: Literal["ok", "error"]
    database: Literal["connected", "disconnected"]
