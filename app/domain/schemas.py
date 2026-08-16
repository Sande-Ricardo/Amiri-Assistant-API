from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ProposalCreateRequest(BaseModel):
    raw_requirements: str = Field(
        ...,
        min_length=20,
        description="Unstructured text containing functional and technical client requirements.",
        json_schema_extra={
            "example": (
                "We need an e-commerce inventory management system with monthly automated "
                "reports, email notifications when stock is low, and multi-warehouse support."
            )
        },
    )
    client_name: str | None = Field(
        default=None,
        description="Optional name of the client or requesting company.",
        json_schema_extra={"example": "Comercial Andina S.A."},
    )


class ProposalCreateResponse(BaseModel):
    request_id: UUID = Field(
        ...,
        description="Unique UUID identifying the generation request.",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"},
    )
    status: Literal["pending", "processing", "completed", "failed"] = Field(
        ...,
        description="Current status of the proposal generation lifecycle.",
        json_schema_extra={"example": "pending"},
    )
    status_check_url: str = Field(
        ...,
        description="Relative URL to poll for pipeline progress and completion.",
        json_schema_extra={
            "example": "/api/v1/proposals/123e4567-e89b-12d3-a456-426614174000/status"
        },
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the request was accepted (ISO 8601).",
        json_schema_extra={"example": "2026-08-16T12:00:00Z"},
    )


class ProposalData(BaseModel):
    final_markdown: str = Field(
        ...,
        description="Complete commercial proposal document compiled in Markdown format.",
        json_schema_extra={
            "example": "# Commercial Proposal\n\n## Executive Summary\n..."
        },
    )
    total_estimated_hours: int = Field(
        ...,
        description="Recalculated sum of development hours across all proposed modules.",
        json_schema_extra={"example": 160},
    )
    suggested_tech_stack: dict[str, Any] = Field(
        ...,
        description="Categorized tech stack inferred for the solution.",
        json_schema_extra={
            "example": {
                "backend": "FastAPI (Python 3.11)",
                "database": "PostgreSQL",
                "hosting": "Render",
            }
        },
    )
    identified_ambiguities: list[str] = Field(
        ...,
        description="List of ambiguities or requirements gaps detected by the Analyst Agent.",
        json_schema_extra={
            "example": ["Unspecified expected monthly order volume."]
        },
    )
    resolved_assumptions: list[str] = Field(
        ...,
        description="Assumptions documented by the Architect Agent to resolve ambiguities.",
        json_schema_extra={
            "example": [
                "Assumed up to 10,000 monthly orders based on standard SMB size."
            ]
        },
    )


class ProposalStatusResponse(BaseModel):
    request_id: UUID = Field(
        ...,
        description="Unique request UUID identifier.",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"},
    )
    status: Literal["pending", "processing", "completed", "failed"] = Field(
        ...,
        description="Current status of the proposal generation pipeline.",
        json_schema_extra={"example": "completed"},
    )
    current_node: str | None = Field(
        default=None,
        description="Currently executing agent node (analyst_agent, architect_agent, writer_agent).",
        json_schema_extra={"example": "writer_agent"},
    )
    proposal: ProposalData | None = Field(
        default=None,
        description="Full generated proposal payload. Present only when status is 'completed'.",
    )
    error_message: str | None = Field(
        default=None,
        description="Error detail when pipeline execution fails. Present only when status is 'failed'.",
        json_schema_extra={"example": None},
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the request was initiated (ISO 8601).",
        json_schema_extra={"example": "2026-08-16T12:00:00Z"},
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp of the last status update (ISO 8601).",
        json_schema_extra={"example": "2026-08-16T12:01:30Z"},
    )


class HealthCheckResponse(BaseModel):
    status: Literal["ok", "error"] = Field(
        ...,
        description="Overall service operational status.",
        json_schema_extra={"example": "ok"},
    )
    database: Literal["connected", "disconnected"] = Field(
        ...,
        description="MySQL database connection status.",
        json_schema_extra={"example": "connected"},
    )
