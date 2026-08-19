from typing import Any
from uuid import UUID, uuid4

from fastapi import BackgroundTasks

from app.agents.graph import run_proposal_pipeline
from app.ports.repositories import ProposalRepositoryPort


class ProposalService:
    def __init__(self, repository: ProposalRepositoryPort) -> None:
        self.repository = repository

    async def initiate_generation(
        self,
        raw_requirements: str,
        client_name: str | None,
        background_tasks: BackgroundTasks,
    ) -> UUID:
        # UUID v4 generated at the application layer, following hexagonal architecture
        request_id = uuid4()

        self.repository.create_request(
            request_id=request_id,
            raw_requirements=raw_requirements,
            client_name=client_name,
        )

        background_tasks.add_task(
            run_proposal_pipeline,
            request_id=request_id,
            raw_requirements=raw_requirements,
            client_name=client_name,
        )

        return request_id

    async def check_status(self, request_id: UUID) -> dict[str, Any] | None:
        return self.repository.get_request_by_id(request_id)
