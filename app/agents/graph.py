from typing import Any
from uuid import UUID

from langgraph.graph import END, START, StateGraph

from app.agents.analyst import run_analyst_agent
from app.agents.architect import run_architect_agent
from app.agents.state import ProposalGenerationState
from app.agents.writer import run_writer_agent


def analyst_node(state: ProposalGenerationState) -> dict[str, Any]:
    """
    Analyst node wrapper. Extracts clean requirements and ambiguities.
    """
    raw_reqs = state.get("raw_requirements", "")
    client = state.get("client_name")

    result = run_analyst_agent(raw_requirements=raw_reqs, client_name=client)

    return {
        "clean_requirements": result.clean_requirements,
        "identified_ambiguities": result.identified_ambiguities,
        "current_node": "analyst_agent",
    }


def architect_node(state: ProposalGenerationState) -> dict[str, Any]:
    """
    Architect node wrapper. Defines tech stack, modules, and hours.
    """
    clean_reqs = state.get("clean_requirements", [])
    ambiguities = state.get("identified_ambiguities", [])

    result = run_architect_agent(
        clean_requirements=clean_reqs,
        identified_ambiguities=ambiguities,
    )

    return {
        "suggested_tech_stack": result.suggested_tech_stack,
        "resolved_assumptions": result.resolved_assumptions,
        "proposed_modules": result.proposed_modules,
        "total_estimated_hours": result.total_estimated_hours,
        "current_node": "architect_agent",
    }


def writer_node(state: ProposalGenerationState) -> dict[str, Any]:
    """
    Writer node wrapper. Compiles full markdown proposal.
    """
    clean_reqs = state.get("clean_requirements", [])
    tech_stack = state.get("suggested_tech_stack", {})
    assumptions = state.get("resolved_assumptions", [])
    modules = state.get("proposed_modules", [])
    total_hours = state.get("total_estimated_hours", 0)
    client = state.get("client_name")

    markdown = run_writer_agent(
        clean_requirements=clean_reqs,
        suggested_tech_stack=tech_stack,
        resolved_assumptions=assumptions,
        proposed_modules=modules,
        total_estimated_hours=total_hours,
        client_name=client,
    )

    return {
        "final_markdown": markdown,
        "current_node": "writer_agent",
        "status": "completed",
    }


def create_proposal_graph() -> Any:
    """
    Constructs and compiles the proposal generation StateGraph DAG pipeline.
    """
    workflow = StateGraph(ProposalGenerationState)

    # Add nodes
    workflow.add_node("analyst_agent", analyst_node)
    workflow.add_node("architect_agent", architect_node)
    workflow.add_node("writer_agent", writer_node)

    # Define sequential edges
    workflow.add_edge(START, "analyst_agent")
    workflow.add_edge("analyst_agent", "architect_agent")
    workflow.add_edge("architect_agent", "writer_agent")
    workflow.add_edge("writer_agent", END)

    return workflow.compile()


# Export compiled graph application instance
proposal_pipeline_app = create_proposal_graph()


async def run_proposal_pipeline(
    request_id: UUID, raw_requirements: str, client_name: str | None
) -> dict[str, Any]:
    """
    Runner function to execute the compiled LangGraph pipeline.
    """
    initial_state: ProposalGenerationState = {
        "request_id": request_id,
        "raw_requirements": raw_requirements,
        "client_name": client_name,
        "status": "processing",
        "current_node": "analyst_agent",
    }

    final_state = await proposal_pipeline_app.ainvoke(initial_state)
    return dict(final_state)
