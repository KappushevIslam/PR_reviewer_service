# PR Reviewer Assignment Service

Микросервис автоматического назначения ревьюеров на Pull Request'ы.

## Технологический стек

- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Docker

## Запуск

```bash
docker-compose up
```

Сервис доступен на http://localhost:8080

Документация API: http://localhost:8080/docs

## API Endpoints

### Teams

- `POST /team/add` - создание команды с участниками
- `GET /team/get` - получение команды
- `POST /team/deactivateUsers` - массовая деактивация пользователей с переназначением PR

### Users

- `POST /users/setIsActive` - изменение статуса активности
- `GET /users/getReview` - список PR пользователя

### Pull Requests

- `POST /pullRequest/create` - создание PR с автоназначением до 2 ревьюеров
- `POST /pullRequest/merge` - merge PR (идемпотентная операция)
- `POST /pullRequest/reassign` - переназначение ревьювера

### Statistics

- `GET /statistics` - статистика по PR и назначениям

### Health

- `GET /health` - проверка состояния сервиса

## Бизнес-логика

### Автоназначение ревьюеров

При создании PR автоматически назначаются до 2 активных участников команды автора, исключая самого автора. Если доступных кандидатов меньше двух, назначается доступное количество.

### Переназначение

Заменяет одного ревьювера на случайного активного участника из команды заменяемого ревьювера, исключая автора PR и текущих ревьюеров. После MERGED статуса переназначение запрещено.

### Массовая деактивация

Деактивирует указанных пользователей команды и автоматически переназначает их открытые PR на активных участников. Если кандидатов нет, ревьювер просто удаляется.

## Тестирование

### E2E тесты

make test

Реализованы тесты:

- Полный workflow: создание команды, PR, merge, получение статистики
- Переназначение ревьюеров
- Обработка ошибок
- Массовая деактивация

### Команды (Makefile)

```bash
make build      # Собрать Docker образ
make up         # Запустить сервисы
make down       # Остановить сервисы
make logs       # Просмотр логов
make test       # Запустить тесты
make load-test 	# Нагрузочное тестирование (locust)
make migrate    # Применить миграции
make psql       # Подключиться к PostgreSQL
```

## Линтинг

Конфигурация в `pyproject.toml` и `.flake8`.

```bash
pip install -r requirements-dev.txt
black app/ tests/
isort app/ tests/
flake8 app/ tests/
mypy app/
```

## Переменные окружения

```
POSTGRES_USER=pr_reviewer
POSTGRES_PASSWORD=pr_reviewer_password
POSTGRES_DB=pr_reviewer_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

## Архитектурные решения

**Выбор технологий:**

- FastAPI для автогенерации OpenAPI и валидации
- SQLAlchemy ORM для работы с PostgreSQL
- Alembic для управления миграциями
- Docker Compose для изоляции окружения

**Структура кода:**

- models: определения таблиц БД
- crud: операции с БД
- services: бизнес-логика
- routers: HTTP endpoints
- schemas: валидация запросов/ответов

**Производительность:**

- Индексы на foreign keys и часто используемые поля
- Eager loading (joinedload) для минимизации N+1 запросов
- Connection pooling в SQLAlchemy

**Обработка ошибок:**

- Единый формат ответов согласно OpenAPI спецификации
- Коды ошибок: TEAM_EXISTS, PR_EXISTS, PR_MERGED, NOT_ASSIGNED, NO_CANDIDATE, NOT_FOUND
- Правильные HTTP статусы (404, 409, 400)

## Допущения

1. Случайный выбор ревьюеров через Python random (достаточно для объема данных)
2. Миграции применяются при запуске через docker-compose up
3. При массовой деактивации PR без доступных кандидатов остается без ревьювера
