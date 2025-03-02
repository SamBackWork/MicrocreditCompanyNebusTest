import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routers import organizations, buildings, activities  # Относительный импорт

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)


#  Создаем экземпляр FastAPI *внутри* функции
def create_app():
    """
    Создает и настраивает приложение FastAPI.

    Returns:
        app: Экземпляр приложения FastAPI.
    """
    app = FastAPI(
        title="Organization API",
        description="API for managing organizations, buildings, and activities",
        version="1.0.0",
    )

    # Добавляем middleware для логирования запросов
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """
        Middleware для логирования входящих запросов и кодов ответа.
        """
        logger.info(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response status code: {response.status_code}")
        return response

    # Добавляем роутеры (передаем app)
    app.include_router(organizations.router)
    app.include_router(buildings.router)
    app.include_router(activities.router)

    # Настройка CORS
    origins = ["*"]  # Разрешаем запросы от любых источников

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],  # Разрешаем все методы
        allow_headers=["*"],  # Разрешаем все заголовки
    )

    @app.get("/")
    async def root():
        """
        Корневой эндпоинт, возвращающий приветственное сообщение.
        """
        return {"message": "Welcome to the Organization API"}

    return app


app = create_app()  # Создаем приложение
