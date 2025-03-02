from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения

API_KEY_NAME = "X-API-Key"  # Заголовок, в котором ожидается ключ
API_KEY = os.getenv("API_KEY")  # Получаем ключ из переменной окружения

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def api_key_auth(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
