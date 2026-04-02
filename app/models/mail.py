from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.feature import Feature


class Email(Base, Feature):
    __tablename__ = "emails"

    email: Mapped[str] = mapped_column(String(128), nullable=False)
    subject: Mapped[str] = mapped_column(Text, nullable=False, comment="email theme")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="email body")
    email_files = relationship("EmailFiles")
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    account = relationship("Account", back_populates="email")

    def __repr__(self):
        return self.subject


class EmailFiles(Base):
    __tablename__ = "email_files"

    email_id: Mapped[int] = mapped_column(ForeignKey("emails.id"))
    title: Mapped[str] = mapped_column(String(128))
    url: Mapped[str] = mapped_column(String(128))

    def __repr__(self):
        return self.title

    def save(self, session):
        session.add(self)
        session.commit()
        session.refresh(self)
