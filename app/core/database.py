import ssl
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.core.config import database_uri, debug


class SessionManager:
    def __init__(self) -> None:
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self.database_uri = database_uri

    def init_db(self) -> None:
        connect_args = {}
        if "sslmode" and "sslrootcert" in database_uri:
            cert_path = database_uri.split("sslrootcert=")[1]
            ssl_context = ssl.create_default_context(cafile=cert_path)
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            connect_args["ssl"] = ssl_context
            self.database_uri = database_uri.split("sslmode")[0]

        self.engine = create_async_engine(
            self.database_uri,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=10,
            max_overflow=15,
            pool_pre_ping=True,
            pool_recycle=5,
            echo=debug,
            connect_args=connect_args
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )

    async def close(self) -> None:
        if self.engine:
            await self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self.session_factory:
            raise RuntimeError("Database session factory is not initialized.")

        async with self.session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise RuntimeError(f"Database session error: {e!r}") from e
            finally:
                await session.close()


sessionmanager = SessionManager()
Base = declarative_base()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in sessionmanager.get_session():
        yield session
