from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.ports.repositories import ProposalRepositoryPort


class InMemoryProposalRepository(ProposalRepositoryPort):
    """In-memory mock implementation until database migrations are configured."""

    def __init__(self) -> None:
        self._storage: dict[UUID, dict[str, Any]] = {}

    async def create_request(
        self, raw_requirements: str, client_name: str | None
    ) -> UUID:
        request_id = uuid4()
        now = datetime.now(timezone.utc)
        self._storage[request_id] = {
            "request_id": request_id,
            "status": "pending",
            "raw_requirements": raw_requirements,
            "client_name": client_name,
            "current_node": None,
            "proposal": None,
            "error_message": None,
            "created_at": now,
            "updated_at": now,
        }
        return request_id

    async def get_request_status(self, request_id: UUID) -> dict[str, Any] | None:
        return self._storage.get(request_id)
