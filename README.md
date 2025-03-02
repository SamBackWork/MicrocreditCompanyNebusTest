# Organization API

## Описание

REST API для справочника организаций, зданий и видов деятельности.

## Стэк

*   FastAPI
*   SQLAlchemy
*   PostgreSQL
*   Alembic
*   Docker

## Установка и запуск

1.  Склонируйте репозиторий:
    ```bash
    git clone <repository_url>
    ```
1.  Перейдите в директорию проекта:
    ```bash
    cd MicrocreditCompanyNebus
    ```
3.  Соберите Docker образ:
    ```bash
    docker-compose build
    ```
4.  Запустите контейнеры:
    ```bash
    docker-compose up
    ```
    Или для фонового режима:
    ```bash
    docker-compose up -d
    ```

Приложение будет доступно по адресу `http://localhost:8000`.

Документация API (Swagger UI): `http://localhost:8000/docs`

## Переменные окружения
DATABASE_URL - строка подключения к базе данных.
API_KEY - апи ключ.

## Тестирование
Запустить тесты можно командой:
```bash
  poetry run pytest
```

```

*   **Swagger UI:**  Запусти приложение (`docker-compose up`) и перейди по адресу `http://localhost:8000/docs`.  Убедись, что:
*   Все роуты (`/organizations`, `/buildings`, `/activities`) отображаются.
*   Для каждого роута видны все методы (GET, POST).
*   Для каждого метода видны параметры (path parameters, query parameters, request body).  Нажми "Try it out", повводи данные и проверь, что запросы работают.