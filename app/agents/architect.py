import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.schemas import AmbiguityItem, ArchitectOutputSchema
from app.core.llm_factory import LLMProvider, get_llm

ARCHITECT_SYSTEM_PROMPT = """You are a Principal Software Architect and Solutions Engineer.
Your task is to design a software solution blueprint based on clean requirements and identified ambiguities from the Business Analyst.

Primary Responsibilities:
1. **Resolve Ambiguities via Assumptions**: Review the identified ambiguities and explicitly state realistic, practical business/technical assumptions (`resolved_assumptions`) to resolve them.
2. **Suggest Technology Stack**: Recommend a suitable, modern technical stack categorized by domain (e.g., frontend, backend, database, hosting, AI/ML) tailored to the project requirements.
3. **Define Software Modules & Estimate Hours**: Break down the solution into logical software modules. For each module, provide a clear scope description and realistic development hour estimate.
4. **Calculate Total Hours**: Ensure `total_estimated_hours` is the exact sum of hours across all proposed modules.

Guidelines:
- Ensure module breakdowns cover all clean requirements.
- Be realistic with hour estimates based on industry standards for MVP/software delivery.
- Write clear, professional descriptions for each module.
"""


def run_architect_agent(
    clean_requirements: list[str],
    identified_ambiguities: list[AmbiguityItem | dict[str, Any]],
    llm_provider: LLMProvider | None = None,
) -> ArchitectOutputSchema:
    """
    Executes the Architect Agent to design the solution architecture blueprint.

    Args:
        clean_requirements: List of clean requirement statements.
        identified_ambiguities: List of AmbiguityItem instances or equivalent dicts.
        llm_provider: Optional provider override ('gemini' or 'groq').

    Returns:
        ArchitectOutputSchema containing tech stack, assumptions, modules, and total hours.
    """
    llm = get_llm(provider=llm_provider, temperature=0.0)
    structured_llm = llm.with_structured_output(ArchitectOutputSchema)

    ambiguities_formatted = []
    for item in identified_ambiguities:
        if isinstance(item, AmbiguityItem):
            ambiguities_formatted.append(item.model_dump())
        else:
            ambiguities_formatted.append(item)

    user_content = (
        f"Clean Requirements:\n{json.dumps(clean_requirements, indent=2)}\n\n"
        f"Identified Ambiguities:\n{json.dumps(ambiguities_formatted, indent=2)}"
    )

    messages = [
        SystemMessage(content=ARCHITECT_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    result = structured_llm.invoke(messages)
    if isinstance(result, dict):
        return ArchitectOutputSchema.model_validate(result)
    return result
