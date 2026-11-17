# Изменения для задания PostgreSQL

Реализована замена in-memory хранения на PostgreSQL без изменения URL и форматов API
Assignment 5. Алгоритмы анализа не изменялись. Frontend, авторизация и другие функции
в это изменение не добавлены. Коммит и push не выполнялись.

## Новые файлы

| Файл | Назначение |
|---|---|
| `app/database.py` | Читает DATABASE_URL из окружения/корневого .env, создаёт PostgreSQL Engine и фабрику Session. |
| `app/models.py` | ORM-модели Project, Audit, Finding: UUID, даты с часовым поясом, ограничения, индексы, связи one-to-many и каскады. |
| `.env.example` | Шаблон DATABASE_URL и отдельного TEST_DATABASE_URL без настоящих credentials. |
| `alembic.ini` | Расположение миграций и Python import path относительно репозитория. |
| `alembic/env.py` | Подключение Alembic к той же базе и metadata; поддерживает online/offline режимы. |
| `alembic/script.py.mako` | Шаблон для следующих миграций. |
| `alembic/versions/0001_initial.py` | Версия 0001: создание всех таблиц, внешних ключей, индексов и ограничений; downgrade удаляет таблицы в обратном порядке. |
| `tests/conftest.py` | Реальный PostgreSQL для тестов, применение миграций, очистка отдельной test-базы, TestClient с lifespan. Проверяет суффикс _test и отличие от основной базы. |
| `tests/test_database.py` | Персистентность между экземплярами приложения, FK/CHECK, rollback, каскады, конкурирующие дубликаты, downgrade/upgrade/check. |
| `docs/swagger-postgresql-results.json` | Фактические ответы после нажатий Execute в Swagger UI. |
| `docs/swagger-postgresql.jpg` | Скриншот проверки ответа после каскадного удаления. |
| `docs/database-changes.md` | Этот перечень файлов и объяснения. |

## Изменённые файлы

| Файл | Что изменено и зачем |
|---|---|
| `app/main.py` | Lifespan создаёт Engine/sessionmaker и освобождает пул при завершении; MemoryStore удалён. |
| `app/api/dependencies.py` | Session и транзакция на запрос: commit при успехе, rollback при ошибке, закрытие всегда. IntegrityError преобразуется в 409. |
| `app/api/routes/projects.py` | Получает Session через Depends вместо MemoryStore; сохраняет endpoints и response models. |
| `app/api/routes/audits.py` | Передаёт Session сервисам аудитов/отчёта. |
| `app/api/routes/findings.py` | Передаёт Session сервису findings. |
| `app/services/projects.py` | SELECT/INSERT/UPDATE/DELETE через ORM; поиск и пагинация в БД; name_key для casefold-уникальности; блокировки при изменении/удалении. |
| `app/services/audits.py` | Аудит и findings сохраняются атомарно; чтение и история через SQL. Блокировка родителя предотвращает гонку с удалением проекта. |
| `app/services/findings.py` | SQL-фильтры и пагинация; изменение статуса с блокировкой строки; отчёт вычисляется из записей БД. |
| `app/schemas/projects.py` | ProjectRead читает ORM-атрибуты через from_attributes; входные правила сохранены. |
| `app/schemas/audits.py` | AuditRead читает ORM-атрибуты. |
| `app/schemas/findings.py` | FindingRead читает ORM-атрибуты. |
| `requirements.txt` | SQLAlchemy, Alembic, psycopg binary, python-dotenv; минимальный FastAPI повышен для Depends(scope="function"). |
| `tests/test_api.py` | Прежние три сценария используют PostgreSQL fixture вместо in-memory приложения. |
| `README.md` | Установка/настройка PostgreSQL, .env, миграции, запуск, тестовая база и результаты проверки. |
| `docs/architecture.md` | Описание ORM, транзакций, ограничений и связей вместо временного хранилища. |
| `docs/swagger-checklist.md` | Проверка сохранения после перезапуска и фактические результаты нового Swagger-прогона. |

## Удалённый файл

`app/repositories/memory.py` — старые словари и RLock больше не используются.
При переносе архива изменений на другую копию репозитория этот файл нужно удалить.

## Локальная настройка, не для Git

Создан `.env` с адресами локальных баз `bitrate` и `bitrate_test` на порту 55432.
Он уже исключён существующим .gitignore и не включён в архив изменений.
Установлены PostgreSQL 17.12 через Homebrew и Python-зависимости в `../.venv`.
Не добавляйте .env, виртуальное окружение или каталог PostgreSQL в Git.

## Проверка 17 ноября 2026

- `alembic upgrade head` → 0001; `alembic check` → нет отличий схемы от моделей.
- 7 интеграционных тестов на PostgreSQL: passed.
- Все 12 API-операций выполнены через Swagger, включая 201/200/204, 404/409/422.
- Настоящий перезапуск Uvicorn не потерял проект, аудит, статус finding и комментарий.
- Downgrade/upgrade в отдельной тестовой базе восстановил работоспособную схему.
- Сохранилось только deprecation warning Starlette о httpx-адаптере TestClient.

Для сдачи остаются ваш коммит, push и отправка ссылки на Moodle.
