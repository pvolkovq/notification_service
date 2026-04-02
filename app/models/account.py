from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    realm: Mapped[str] = mapped_column(String(255), nullable=True)
    uri: Mapped[str] = mapped_column(String(255), nullable=True)
    host: Mapped[str] = mapped_column(String(255), nullable=True)
    port: Mapped[str] = mapped_column(String(5), nullable=True)
    login: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    token: Mapped[str] = mapped_column(String(255), nullable=True)
    certificate: Mapped[str] = mapped_column(Text, nullable=True)
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict())
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    integration_id: Mapped[int] = mapped_column(ForeignKey("integrations.id"))
    integration: Mapped["Integration"] = relationship(
        back_populates="accounts", lazy="selectin"
    )

    call = relationship("Call", back_populates="account", uselist=False)
    message = relationship("Message", back_populates="account", uselist=False)
    push = relationship("Push", back_populates="account", uselist=False)
    email = relationship("Email", back_populates="account", uselist=False)

    def __repr__(self):
        return f"id: {self.id} | name: {self.name}"
