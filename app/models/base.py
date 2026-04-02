from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    async def all(cls, session: AsyncSession):
        result = await session.execute(select(cls))
        return result.scalars().all()

    @classmethod
    async def filter(cls, session: AsyncSession, **filters):
        result = await session.execute(select(cls).filter_by(**filters))
        return result.scalars().all()

    @classmethod
    async def get(cls, session: AsyncSession, id: int):
        return await session.get(cls, id)


class CreatedUpdated:
    created_at: Mapped[str] = mapped_column(server_default=func.now())
    updated_at: Mapped[str] = mapped_column(nullable=True, onupdate=func.now())
