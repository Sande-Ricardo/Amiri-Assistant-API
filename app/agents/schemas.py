from pydantic import BaseModel, Field


class AmbiguityItem(BaseModel):
    """Represents a specific requirement ambiguity or missing specification."""

    point: str = Field(
        ...,
        description="The ambiguous point or unclear requirement identified in the text.",
    )
    question: str = Field(
        ...,
        description="The clarifying question to resolve this ambiguity.",
    )


class AnalystOutputSchema(BaseModel):
    """Structured output expected from the Analyst Agent."""

    clean_requirements: list[str] = Field(
        ...,
        description=(
            "List of clean, unambiguous functional and technical requirements "
            "extracted from the raw input."
        ),
    )
    identified_ambiguities: list[AmbiguityItem] = Field(
        default_factory=list,
        description=(
            "List of ambiguities, missing details, or assumptions that require resolution."
        ),
    )


class ModuleItem(BaseModel):
    """Represents a proposed software module with its estimated development effort."""

    name: str = Field(
        ...,
        description="Name of the software module or component (e.g., 'Authentication Module').",
    )
    description: str = Field(
        ...,
        description="Brief summary of features, scope, and technical responsibilities of this module.",
    )
    estimated_hours: int = Field(
        ...,
        gt=0,
        description="Estimated development effort in hours for this module.",
    )


class ArchitectOutputSchema(BaseModel):
    """Structured output expected from the Architect Agent."""

    suggested_tech_stack: dict[str, str] = Field(
        ...,
        description=(
            "Recommended technical stack categorized by domain "
            "(e.g., {'frontend': 'React', 'backend': 'FastAPI', 'database': 'PostgreSQL'})."
        ),
    )
    resolved_assumptions: list[str] = Field(
        default_factory=list,
        description=(
            "List of explicit assumptions made by the architect to resolve the identified ambiguities."
        ),
    )
    proposed_modules: list[ModuleItem] = Field(
        ...,
        description="List of proposed software architecture modules with individual hour estimates.",
    )
    total_estimated_hours: int = Field(
        ...,
        gt=0,
        description="Total sum of estimated hours across all proposed modules.",
    )
