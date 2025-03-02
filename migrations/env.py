from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from dotenv import load_dotenv
from app.database import Base  # Импортируем Base из app.database
from alembic import context
import os, sys

# Добавляем текущую директорию в sys.path, чтобы Alembic мог найти модели.
sys.path.append(os.getcwd())

# Загружаем переменные окружения из .env файла.
load_dotenv()

# Получаем объект конфигурации Alembic.
config = context.config

# Настраиваем логгирование, если есть файл конфигурации.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Получаем метаданные из Base, чтобы Alembic мог сгенерировать миграции.
target_metadata = Base.metadata  # Moved this here for clarity


def run_migrations_offline() -> None:
    url = os.getenv("DATABASE_URL")  # Получаем URL из переменной окружения
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL")) #
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Определяем, в каком режиме запускаются миграции (online или offline).
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
