from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import CreatedUpdated


class Feature(CreatedUpdated):
    __abstract__ = True

    PENDING = "pending"
    IN_PROCESS = "in_process"
    COMPLETED = "completed"
    FAILED = "failed"
    TYPES = [
        PENDING,
        IN_PROCESS,
        COMPLETED,
        FAILED,
    ]

    status: Mapped[str] = mapped_column(String(11), nullable=False)
    options: Mapped[JSONB] = mapped_column(JSONB, default={})
    log: Mapped[str] = mapped_column(
        Text, nullable=True, comment="log in format {time:action:response}"
    )

    def save(self, session):
        session.add(self)
        session.commit()
        session.refresh(self)
