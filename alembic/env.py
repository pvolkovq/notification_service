from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context
from app.core.config import database_uri
from app.models import *  # noqa: F403
from app.models.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

database_sync_uri = database_uri.replace("+asyncpg", "")


def run_migrations_offline() -> None:
    context.configure(
        url=database_sync_uri,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(database_sync_uri, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
