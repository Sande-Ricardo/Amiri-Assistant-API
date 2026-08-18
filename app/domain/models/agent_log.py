import enum
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import Base


class AgentNodeName(str, enum.Enum):
    analyst_agent = "analyst_agent"
    architect_agent = "architect_agent"
    writer_agent = "writer_agent"


class AgentExecutionStatus(str, enum.Enum):
    success = "success"
    error = "error"


class AgentExecutionLog(Base):
    """
    ORM model for the 'agent_execution_logs' table.
    Audit trail of every LangGraph node executed.
    Used for observability and debugging.
    """

    __tablename__ = "agent_execution_logs"
    __table_args__ = (
        Index("idx_logs_request_id", "request_id"),
        Index("idx_logs_node_name", "node_name"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    # Auto-incremented surrogate key (no UUID needed here — high-write audit table)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign key to the originating request (cascades on delete)
    request_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("requests.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Name of the executed agent node
    node_name: Mapped[AgentNodeName] = mapped_column(
        Enum(AgentNodeName, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )

    # Snapshot of the LangGraph state before node execution
    input_state_snapshot: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    # Snapshot of the LangGraph state after node execution
    output_state_snapshot: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    # Wall-clock execution time of the node in milliseconds
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Estimated total token count consumed during this node execution
    tokens_used_estimate: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Outcome of the node execution
    status: Mapped[AgentExecutionStatus] = mapped_column(
        Enum(AgentExecutionStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )

    # Full error traceback when status='error'
    error_trace: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
