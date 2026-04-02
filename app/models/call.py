from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.feature import Feature


class Call(Base, Feature):
    __tablename__ = "calls"

    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ext_id: Mapped[int] = mapped_column(
        String(50), nullable=True, comment="id from external service"
    )
    ext_status_code: Mapped[int] = mapped_column(
        comment="http status code from external service", nullable=True
    )
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    account = relationship("Account", back_populates="call")

    def __repr__(self):
        return self.content
