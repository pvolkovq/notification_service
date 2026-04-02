from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MessageTemplate(Base):
    __tablename__ = "message_templates"
    PASSWORD = "password"
    VALIDATION_CODE = "validation_code"
    TYPES = [PASSWORD, VALIDATION_CODE]

    type: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
