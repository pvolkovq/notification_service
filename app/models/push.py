from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.feature import Feature


class Push(Base, Feature):
    __tablename__ = "pushes"

    push_token: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="push body")
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    account = relationship("Account", back_populates="push")

    def __repr__(self):
        return self.content
