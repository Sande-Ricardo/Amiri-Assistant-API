# Model registry — import all ORM models here so that Base.metadata
# is fully populated when Alembic's env.py sets target_metadata = Base.metadata.
# This guarantees that alembic revision --autogenerate detects all tables.

from app.domain.models.agent_log import AgentExecutionLog, AgentExecutionStatus, AgentNodeName
from app.domain.models.base import Base
from app.domain.models.proposal import Proposal
from app.domain.models.request import RequestRecord, RequestStatus

__all__ = [
    "Base",
    "RequestRecord",
    "RequestStatus",
    "Proposal",
    "AgentExecutionLog",
    "AgentNodeName",
    "AgentExecutionStatus",
]
