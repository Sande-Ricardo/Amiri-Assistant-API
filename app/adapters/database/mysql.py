from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.ports.repositories import AgentLogRepositoryPort, ProposalRepositoryPort


class InMemoryProposalRepository(ProposalRepositoryPort):
    """
    In-memory mock implementation of ProposalRepositoryPort.
    Retained for local development and unit testing without a live database.
    """

    def __init__(self) -> None:
        self._storage: dict[UUID, dict[str, Any]] = {}
        self._proposals: dict[UUID, dict[str, Any]] = {}

    def create_request(
        self,
        request_id: UUID,
        raw_requirements: str,
        client_name: str | None,
    ) -> None:
        now = datetime.now(timezone.utc)
        self._storage[request_id] = {
            "request_id": request_id,
            "status": "pending",
            "raw_requirements": raw_requirements,
            "client_name": client_name,
            "current_node": None,
            "error_message": None,
            "llm_provider_used": None,
            "proposal": None,
            "created_at": now,
            "updated_at": now,
        }

    def get_request_by_id(self, request_id: UUID) -> dict[str, Any] | None:
        record = self._storage.get(request_id)
        if record is None:
            return None
        result = dict(record)
        result["proposal"] = self._proposals.get(request_id)
        return result

    def update_request_status(
        self,
        request_id: UUID,
        status: str,
        current_node: str | None = None,
        error_message: str | None = None,
        llm_provider_used: str | None = None,
    ) -> None:
        if request_id not in self._storage:
            return
        self._storage[request_id]["status"] = status
        self._storage[request_id]["current_node"] = current_node
        self._storage[request_id]["error_message"] = error_message
        self._storage[request_id]["llm_provider_used"] = llm_provider_used
        self._storage[request_id]["updated_at"] = datetime.now(timezone.utc)

    def save_proposal(
        self,
        request_id: UUID,
        proposal_id: UUID,
        clean_requirements: list[str],
        identified_ambiguities: list[dict[str, Any]],
        resolved_assumptions: list[str],
        suggested_tech_stack: dict[str, str],
        proposed_modules: list[dict[str, Any]],
        total_estimated_hours: int,
        final_markdown: str,
    ) -> None:
        now = datetime.now(timezone.utc)
        self._proposals[request_id] = {
            "id": str(proposal_id),
            "final_markdown": final_markdown,
            "total_estimated_hours": total_estimated_hours,
            "suggested_tech_stack": suggested_tech_stack,
            "identified_ambiguities": identified_ambiguities,
            "resolved_assumptions": resolved_assumptions,
        }
        self._storage[request_id]["status"] = "completed"
        self._storage[request_id]["updated_at"] = now


class InMemoryAgentLogRepository(AgentLogRepositoryPort):
    """
    In-memory mock implementation of AgentLogRepositoryPort.
    Retained for local development and unit testing without a live database.
    """

    def __init__(self) -> None:
        self._logs: list[dict[str, Any]] = []

    def save_agent_log(
        self,
        request_id: UUID,
        node_name: str,
        status: str,
        input_state_snapshot: dict[str, Any] | None = None,
        output_state_snapshot: dict[str, Any] | None = None,
        execution_time_ms: int | None = None,
        tokens_used_estimate: int | None = None,
        error_trace: str | None = None,
    ) -> None:
        self._logs.append(
            {
                "request_id": str(request_id),
                "node_name": node_name,
                "status": status,
                "input_state_snapshot": input_state_snapshot,
                "output_state_snapshot": output_state_snapshot,
                "execution_time_ms": execution_time_ms,
                "tokens_used_estimate": tokens_used_estimate,
                "error_trace": error_trace,
                "created_at": datetime.now(timezone.utc),
            }
        )
