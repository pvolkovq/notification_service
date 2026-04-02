from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Integration(Base):
    __tablename__ = "integrations"

    PUSH = "push"
    MESSAGE = "message"
    CALL = "call"
    EMAIL = "email"
    ANOTHER = "another"

    TYPES = [
        PUSH,
        MESSAGE,
        CALL,
        EMAIL,
        ANOTHER,
    ]

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=True)
    accounts: Mapped[list["Account"]] = relationship(
        back_populates="integration", lazy="selectin"
    )

    def __repr__(self):
        return f"id: {self.id} | name: {self.name} | type: {self.type}"
