from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (если он есть).
load_dotenv()

# Имя заголовка, в котором ожидается API ключ.
API_KEY_NAME = "X-API-Key"
# Получаем API ключ из переменной окружения.
API_KEY = os.getenv("API_KEY")

# Создаем объект APIKeyHeader для извлечения ключа из заголовка.
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def api_key_auth(api_key_header: str = Security(api_key_header)):
    """
    Функция зависимости FastAPI для аутентификации по API ключу.

    Проверяет наличие и корректность API ключа в заголовке запроса.
    """
    if api_key_header == API_KEY:
        return api_key_header  # Возвращаем ключ, если он корректен
    # Если ключ отсутствует или неверен, выбрасываем исключение.
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
