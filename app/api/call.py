from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.clients.call import CallClient
from app.core.database import get_session
from app.models import Call
from app.schemes.call import CallCreate, CheckCall

router = APIRouter()


@router.post("/api/v1/phone_call/", status_code=status.HTTP_201_CREATED)
async def phone_call(
    item: CallCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    client = CallClient(
        to=item.to,
        code=item.code,
        account_id=item.account_id,
        options=item.options,
        session=session,
    )
    background_tasks.add_task(client.process)
    return {"ok": True}


@router.get("/api/v1/check_call/", status_code=status.HTTP_200_OK)
async def check_call(item: CheckCall, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Call).where(Call.phone == item.phone).order_by(desc(Call.created_at))
    )
    call = result.scalars().first()
    if not call:
        return {"msg": f"На номер {item.phone} звонков не было"}
    return call
