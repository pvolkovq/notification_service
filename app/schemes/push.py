from typing import Optional

from pydantic import BaseModel, Field


class PushCreate(BaseModel):
    token: str
    text: str
    options: Optional[dict] = Field(default_factory=dict)
    account_id: Optional[int] = None


class SendPush(BaseModel):
    id: int
    push_token: str
    content: str
    status: str
    options: Optional[dict] = Field(default_factory=dict)
    log: str
