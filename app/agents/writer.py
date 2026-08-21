import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.schemas import ModuleItem
from app.core.llm_factory import LLMProvider, get_llm

WRITER_SYSTEM_PROMPT = """You are a Commercial Proposal Lead and Technical Writer.
Your task is to synthesize requirements analysis and technical software architecture into a comprehensive, professional, high-converting commercial proposal in Markdown format.

Document Structure Guidelines:
1. **Title & Executive Summary**: Clear title, optional client mention, and an executive summary highlighting the value proposition.
2. **Scope of Functional & Technical Requirements**: Cleanly categorized list of project requirements.
3. **Proposed Technical Architecture & Tech Stack**: Bulleted or tabular list of recommended technologies by domain (backend, frontend, database, hosting, etc.).
4. **Modules & Estimation Breakdown**:
   - Create a clean Markdown table summarizing the modules: `| Module Name | Description | Estimated Effort (Hours) |`
   - Include a final summary line or section clearly highlighting the **Total Estimated Effort (Hours)**.
5. **Technical Assumptions & Scope Boundary**: Document explicit technical and business assumptions used to bound the project scope.

Tone & Style Guidelines:
- Professional, persuasive, and authoritative technical tone.
- Clear formatting using standard GitHub-Flavored Markdown (H1, H2, H3, bolding, bullet points, tables).
- Output strictly the raw Markdown proposal without surrounding conversational filler or meta commentary.
"""


def run_writer_agent(
    clean_requirements: list[str],
    suggested_tech_stack: dict[str, str],
    resolved_assumptions: list[str],
    proposed_modules: list[ModuleItem | dict[str, Any]],
    total_estimated_hours: int,
    client_name: str | None = None,
    llm_provider: LLMProvider | None = None,
) -> str:
    """
    Executes the Writer Agent to compile the complete commercial proposal document in Markdown format.

    Args:
        clean_requirements: List of clean requirements.
        suggested_tech_stack: Dict of technical stack items.
        resolved_assumptions: List of architectural assumptions.
        proposed_modules: List of ModuleItem instances or equivalent dicts.
        total_estimated_hours: Sum of estimated hours across modules.
        client_name: Optional name of the client/company.
        llm_provider: Optional provider override ('gemini' or 'groq').

    Returns:
        String containing the full Markdown proposal document.
    """
    llm = get_llm(provider=llm_provider, temperature=0.3)

    modules_formatted = []
    for item in proposed_modules:
        if isinstance(item, ModuleItem):
            modules_formatted.append(item.model_dump())
        else:
            modules_formatted.append(item)

    context_payload = {
        "client_name": client_name or "N/A",
        "clean_requirements": clean_requirements,
        "suggested_tech_stack": suggested_tech_stack,
        "resolved_assumptions": resolved_assumptions,
        "proposed_modules": modules_formatted,
        "total_estimated_hours": total_estimated_hours,
    }

    user_content = (
        f"Synthesize the following project payload into a complete commercial proposal:\n\n"
        f"```json\n{json.dumps(context_payload, indent=2)}\n```"
    )

    messages = [
        SystemMessage(content=WRITER_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    return str(response.content)
