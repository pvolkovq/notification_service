from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.clients.mail import EmailClient
from app.core.database import get_session
from app.schemes.mail import CreateEmail

router = APIRouter()


@router.post("/api/v1/send_email/", status_code=status.HTTP_201_CREATED)
async def send_email(item: CreateEmail, session: AsyncSession = Depends(get_session)):
    client = EmailClient(
        content=item.content,
        to=item.to,
        subject=item.subject,
        files=item.files,
        account_id=item.account_id,
        options=item.options,
        session=session,
    )
    await client.process()
    return {"ok": True}
