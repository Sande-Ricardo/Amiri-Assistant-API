from typing import Any
from uuid import UUID

from app.core.database import SessionLocal
from app.domain.models.agent_log import AgentExecutionLog, AgentExecutionStatus, AgentNodeName
from app.ports.repositories import AgentLogRepositoryPort


class MySQLAgentLogRepository(AgentLogRepositoryPort):
    """
    MySQL adapter implementing AgentLogRepositoryPort via SQLAlchemy ORM.
    Inserts one audit row per LangGraph node execution (success or error).
    Session is self-managed so it can be safely called from BackgroundTasks.
    """

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
        """
        Persists an audit record for a single LangGraph node execution.
        node_name and status are validated against their respective Enum types
        before insertion to catch pipeline bugs early.
        """
        with SessionLocal() as session:
            log_entry = AgentExecutionLog(
                request_id=str(request_id),
                node_name=AgentNodeName(node_name),
                status=AgentExecutionStatus(status),
                input_state_snapshot=input_state_snapshot,
                output_state_snapshot=output_state_snapshot,
                execution_time_ms=execution_time_ms,
                tokens_used_estimate=tokens_used_estimate,
                error_trace=error_trace,
            )
            session.add(log_entry)
            session.commit()
