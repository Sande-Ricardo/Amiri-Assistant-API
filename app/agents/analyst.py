from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.schemas import AnalystOutputSchema
from app.core.llm_factory import LLMProvider, get_llm

ANALYST_SYSTEM_PROMPT = """You are a Senior IT Business Analyst and Requirements Engineer.
Your task is to analyze unstructured project requirements submitted by a client and perform two primary duties:

1. **Extract Clean Requirements**: Convert vague, messy, or conversational text into a list of concise, well-structured, unambiguous functional and technical requirements.
2. **Identify Ambiguities & Missing Details**: Spot any vague statements, missing specifications, scale assumptions, or scope gaps, and formulate precise clarifying questions for each.

Guidelines:
- Maintain high technical standards.
- Do not invent requirements that are not mentioned or implied by the input text.
- If the text is clear and has no obvious ambiguities, `identified_ambiguities` can be an empty list.
- Keep each requirement statement clear and actionable.
"""


def run_analyst_agent(
    raw_requirements: str,
    client_name: str | None = None,
    llm_provider: LLMProvider | None = None,
) -> AnalystOutputSchema:
    """
    Executes the Analyst Agent to process raw requirement input.

    Args:
        raw_requirements: The unstructured input requirements text.
        client_name: Optional name of the client or requesting company.
        llm_provider: Optional provider override ('gemini' or 'groq').

    Returns:
        AnalystOutputSchema containing clean_requirements and identified_ambiguities.
    """
    llm = get_llm(provider=llm_provider, temperature=0.0)
    structured_llm = llm.with_structured_output(AnalystOutputSchema)

    user_content = f"Raw Requirements:\n{raw_requirements}"
    if client_name:
        user_content = f"Client/Company: {client_name}\n\n" + user_content

    messages = [
        SystemMessage(content=ANALYST_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    result = structured_llm.invoke(messages)
    if isinstance(result, dict):
        return AnalystOutputSchema.model_validate(result)
    return result
