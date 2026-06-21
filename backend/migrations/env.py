import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Импортируем все модели чтобы alembic видел их metadata
from core.config import settings
from core.database import Base
import users.models  # noqa: F401
import words.models  # noqa: F401
import game.models   # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url.replace("+asyncpg", "+psycopg2"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=settings.database_url,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(conn=conn, target_metadata=target_metadata)
        )
        async with connection.begin():
            await connection.run_sync(lambda conn: context.run_migrations())


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
