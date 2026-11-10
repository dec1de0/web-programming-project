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
12. Перезапустите сервер: список проектов снова пуст.
