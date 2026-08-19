from typing import Any
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.domain.models.proposal import Proposal
from app.domain.models.request import RequestRecord, RequestStatus
from app.ports.repositories import ProposalRepositoryPort


class MySQLProposalRepository(ProposalRepositoryPort):
    """
    MySQL adapter implementing ProposalRepositoryPort via SQLAlchemy ORM.
    Each method manages its own session lifecycle, making it safe to call
    from FastAPI BackgroundTasks where DI-injected sessions are unavailable.
    """

    def create_request(
        self,
        request_id: UUID,
        raw_requirements: str,
        client_name: str | None,
    ) -> None:
        """Persists a new proposal request in 'pending' status."""
        with SessionLocal() as session:
            record = RequestRecord(
                id=str(request_id),
                raw_requirements=raw_requirements,
                client_name=client_name,
                status=RequestStatus.pending,
            )
            session.add(record)
            session.commit()

    def get_request_by_id(self, request_id: UUID) -> dict[str, Any] | None:
        """
        Retrieves a request record and its associated proposal (if completed).
        Returns a normalized dict compatible with ProposalStatusResponse.
        """
        with SessionLocal() as session:
            record: RequestRecord | None = session.get(RequestRecord, str(request_id))
            if record is None:
                return None

            proposal_data: dict[str, Any] | None = None
            if record.status == RequestStatus.completed:
                proposal: Proposal | None = (
                    session.query(Proposal)
                    .filter(Proposal.request_id == str(request_id))
                    .first()
                )
                if proposal:
                    proposal_data = {
                        "final_markdown": proposal.final_markdown,
                        "total_estimated_hours": proposal.total_estimated_hours,
                        "suggested_tech_stack": proposal.suggested_tech_stack_json or {},
                        "identified_ambiguities": proposal.identified_ambiguities_json or [],
                        "resolved_assumptions": proposal.resolved_assumptions_json or [],
                    }

            return {
                "request_id": UUID(record.id),
                "status": record.status.value,
                "current_node": record.current_node,
                "error_message": record.error_message,
                "proposal": proposal_data,
                "created_at": record.created_at,
                "updated_at": record.updated_at,
            }

    def update_request_status(
        self,
        request_id: UUID,
        status: str,
        current_node: str | None = None,
        error_message: str | None = None,
        llm_provider_used: str | None = None,
    ) -> None:
        """Updates the lifecycle fields of an existing request record."""
        with SessionLocal() as session:
            record: RequestRecord | None = session.get(RequestRecord, str(request_id))
            if record is None:
                raise SQLAlchemyError(
                    f"RequestRecord with id={request_id} not found during status update."
                )
            record.status = RequestStatus(status)
            record.current_node = current_node
            record.error_message = error_message
            record.llm_provider_used = llm_provider_used
            session.commit()

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
        """
        Persists the Writer Agent's final output as a Proposal row
        and sets the parent request status to 'completed'.
        Both writes are committed in a single transaction.
        """
        with SessionLocal() as session:
            proposal = Proposal(
                id=str(proposal_id),
                request_id=str(request_id),
                clean_requirements_json=clean_requirements,
                identified_ambiguities_json=identified_ambiguities,
                resolved_assumptions_json=resolved_assumptions,
                suggested_tech_stack_json=suggested_tech_stack,
                proposed_modules_json=proposed_modules,
                total_estimated_hours=total_estimated_hours,
                final_markdown=final_markdown,
            )
            session.add(proposal)

            record: RequestRecord | None = session.get(RequestRecord, str(request_id))
            if record:
                record.status = RequestStatus.completed
                record.current_node = None

            session.commit()
