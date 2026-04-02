from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.clients.push import PushClient
from app.core.database import get_session
from app.models import Push
from app.schemes.push import PushCreate
from app.utils.status import get_status

router = APIRouter()


@router.post("/api/v1/send_push/", status_code=status.HTTP_201_CREATED)
async def send_push(item: PushCreate, session: AsyncSession = Depends(get_session)):
    client = PushClient(
        token=item.token,
        text=item.text,
        account_id=item.account_id,
        options=item.options,
        session=session,
    )
    push_id = await client.process()
    result = await session.execute(select(Push).where(Push.id == push_id))
    if result:
        push = result.scalar_one()
        return get_status(push)
