from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CallCreate(BaseModel):
    to: str
    code: str
    account_id: Optional[int] = None
    options: Optional[dict] = Field(default_factory=dict)


class SendCall(BaseModel):
    id: int
    phone: str
    ext_id: str
    ext_status_code: int
    status: str
    options: Optional[dict] = Field(default_factory=dict)
    log: str
    created_at: datetime


class CallRetrieveStatus(BaseModel):
    id: int
    status: int
    extendStatus: Optional[str]


class CheckCall(BaseModel):
    phone: str
