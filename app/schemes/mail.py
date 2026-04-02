from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CreateEmail(BaseModel):
    to: EmailStr
    subject: str
    content: str
    files: Optional[list[dict]] = Field(default_factory=list)
    account_id: Optional[int] = None
    options: Optional[dict] = Field(default_factory=dict)


class SendEmailFiles(BaseModel):
    id: int
    title: str
    url: str


class SendEmail(BaseModel):
    id: int
    email: str
    subject: str
    content: str
    status: str
    options: Optional[dict] = Field(default_factory=dict)
    log: str
    created_at: datetime
