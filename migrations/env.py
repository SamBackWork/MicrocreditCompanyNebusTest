from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from dotenv import load_dotenv
from app.database import Base
from alembic import context
import os, sys

sys.path.append(os.getcwd())
load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata  # Moved this here for clarity


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Use the DATABASE_URL from the environment variables.
    url = os.getenv("DATABASE_URL")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # Set sqlalchemy.url dynamically from the environment variable.
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))  # Вот оно!

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        # url=os.getenv('DATABASE_URL')  #  Удаляем, URL уже установлен!
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()