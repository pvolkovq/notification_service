from typing import Optional

from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    key: Optional[str] = None
    to: str
    text: str
    account_id: Optional[int] = None
    options: Optional[dict] = Field(default_factory=dict)


class MessageStatus(BaseModel):
    code: str
    operator: str
    channel: Optional[str] = None
