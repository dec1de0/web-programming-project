# Ручная проверка в Swagger UI

Запустите сервер по инструкции в README и откройте <http://127.0.0.1:8000/docs>. Для каждого пункта используйте **Try it out → Execute**. Это чеклист для ручной демонстрации; автоматические проверки находятся в `tests/test_api.py`.

1. `GET /health` → 200.
2. `POST /api/v1/projects`: `{"name":"Demo"}` → 201. Сохраните `id`.
3. Повторите имя как `demo` → 409; отправьте пустое имя → 422.
4. `GET /api/v1/projects` и `GET /api/v1/projects/{project_id}` → 200; проверьте `search`, `offset`, `limit`. `limit=0` → 422.
5. `PATCH /api/v1/projects/{project_id}`: `{"description":"Updated"}` → 200; пустой объект → 422.
6. `POST /api/v1/projects/{project_id}/audits`: отправьте оба примера из README по очереди → 201. Для отсутствующего проекта → 404; неверный `kind` → 422.
7. `GET /api/v1/projects/{project_id}/audits` → 200; проверьте фильтр `kind=code`.
8. `GET /api/v1/audits/{audit_id}`, `GET /api/v1/audits/{audit_id}/findings` и `GET /api/v1/audits/{audit_id}/report` → 200. Проверьте фильтры `severity` и `status`.
9. `PATCH /api/v1/audits/{audit_id}/findings/{finding_id}`: `{"status":"resolved","resolution_note":"Исправлено"}` → 200; без комментария → 422; повторно → 409. `{"status":"open"}` → 200.
10. Сравните оценки отчёта до и после смены статуса.
11. `DELETE /api/v1/projects/{project_id}` → 204; повторное удаление → 404. Запросы его аудитов, замечаний и отчётов → 404.
12. До удаления проекта перезапустите backend. Проект, аудиты, findings и их статусы должны сохраниться.


## Выполнено 17 ноября 2026: PostgreSQL 17.12

Реальный Swagger UI на порту 8001: health; создание проекта (201), дубликат имени (409),
пустое имя (422); список и получение проекта; PATCH описания; создание code-аудита;
история и получение аудита; список findings; PATCH resolved; report (60 → 80).
После остановки и запуска Uvicorn проект, описание, аудит, комментарий и баллы сохранились.
Повтор resolved → 409. DELETE проекта → 204; GET проекта и report после удаления → 404.
Таким образом выполнены все 12 операций. Design-сценарий и дополнительные ограничения
проверены автоматизированными тестами на той же PostgreSQL, в отдельной базе.

Полный текст ответов: `swagger-postgresql-results.json`; скриншот: `swagger-postgresql.jpg`.
Автоматизированные проверки: 7 passed; Alembic check — нет отличий от ORM-моделей;
downgrade base → upgrade head успешно восстанавливает таблицы в тестовой базе.
Имеется предупреждение Starlette об устаревании httpx TestClient, не ошибка приложения.
