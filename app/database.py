# app/database.py
import os
from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base  # Устарело!
from sqlalchemy.orm import declarative_base  # Вот так правильно!
from sqlalchemy.orm import sessionmaker


def get_database_url():
    return os.getenv("DATABASE_URL")


DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
