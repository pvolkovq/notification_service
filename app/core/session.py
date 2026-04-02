from app.core.database import get_session


def connection(method):
    async def wrapper(*args, **kwargs):
        async for session in get_session():
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    return wrapper
