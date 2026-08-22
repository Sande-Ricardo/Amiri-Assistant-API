from typing import TypedDict
from uuid import UUID

from app.agents.schemas import AmbiguityItem, ModuleItem


class ProposalGenerationState(TypedDict, total=False):
    """
    State dictionary passed between LangGraph agent nodes during proposal generation.

    Attributes:
        request_id: Unique UUID of the proposal generation request.
        raw_requirements: Original input requirements text provided by the user.
        client_name: Optional name of the client/company.
        clean_requirements: Refined functional & technical requirements extracted by Analyst Agent.
        identified_ambiguities: Requirement gaps or ambiguous points identified by Analyst Agent.
        suggested_tech_stack: Recommended technical stack mapping created by Architect Agent.
        resolved_assumptions: Technical assumptions made by Architect Agent to resolve ambiguities.
        proposed_modules: List of software modules with scope and hour estimates.
        total_estimated_hours: Recalculated total development hours across all modules.
        final_markdown: Full commercial proposal document in Markdown format compiled by Writer Agent.
        status: Current pipeline execution status ('pending', 'processing', 'completed', 'failed').
        current_node: Name of the currently executing LangGraph node.
        error_message: Detailed error message if execution fails.
        llm_provider_used: LLM provider utilized ('gemini' or 'groq').
    """

    # Input Fields
    request_id: UUID
    raw_requirements: str
    client_name: str | None

    # Analyst Agent Outputs
    clean_requirements: list[str]
    identified_ambiguities: list[AmbiguityItem]

    # Architect Agent Outputs
    suggested_tech_stack: dict[str, str]
    resolved_assumptions: list[str]
    proposed_modules: list[ModuleItem]
    total_estimated_hours: int

    # Writer Agent Outputs
    final_markdown: str

    # Pipeline Metadata & State Tracking
    status: str
    current_node: str | None
    error_message: str | None
    llm_provider_used: str | None
