import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, String, Text, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.base import Base


class RequestStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class RequestRecord(Base):
    """
    ORM model for the 'requests' table.
    Records each proposal generation request and its lifecycle through the agent pipeline.
    """

    __tablename__ = "requests"
    __table_args__ = (
        Index("idx_requests_status", "status"),
        Index("idx_requests_created_at", "created_at"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    # UUID v4 generated at the application layer
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Optional client or company name
    client_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Original unstructured requirements text submitted by the user
    raw_requirements: Mapped[str] = mapped_column(LONGTEXT, nullable=False)

    # Lifecycle status of the request
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=RequestStatus.pending,
        server_default=RequestStatus.pending.value,
    )

    # Name of the LangGraph node currently executing (for granular polling)
    current_node: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Error detail when status='failed'
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # LLM provider actually used ('gemini' | 'groq')
    llm_provider_used: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
