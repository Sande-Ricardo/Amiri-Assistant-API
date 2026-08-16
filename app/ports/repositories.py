from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class ProposalRepositoryPort(ABC):
    @abstractmethod
    async def create_request(
        self, raw_requirements: str, client_name: str | None
    ) -> UUID:
        """Creates a new proposal request in pending state."""
        pass

    @abstractmethod
    async def get_request_status(self, request_id: UUID) -> dict[str, Any] | None:
        """Retrieves request status and result."""
        pass
