import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


def get_database_url():
    """Получает URL базы данных из переменной окружения DATABASE_URL."""
    return os.getenv("DATABASE_URL")


DATABASE_URL = get_database_url()

# Создаем движок SQLAlchemy.
engine = create_engine(DATABASE_URL)

# Создаем класс SessionLocal, который будет использоваться для создания сессий базы данных.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для декларативных моделей.
Base = declarative_base()


def get_db():
    """
    Функция-генератор для получения сессии базы данных.

    Используется в зависимостях FastAPI для внедрения сессии в роуты.
    Автоматически закрывает сессию после завершения запроса.
    """
    db = SessionLocal()
    try:
        yield db  # Возвращаем сессию
    finally:
        db.close()  # Закрываем сессию
