python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload

app/
  main.py                 # Инициализация приложения и регистрация маршрутов
  errors.py               # Описание ошибок приложения
  api/
    router.py             # Маршруты с общим префиксом /api/v1
    dependencies.py       # Доступ к хранилищу и сервисам
    error_handlers.py     # Обработка ошибок и HTTP-ответов
    routes/               # Маршруты health, projects, audits, findings
  schemas/                # Pydantic-модели входных и выходных данных
  services/               # Бизнес-логика, анализ и формирование отчётов
  repositories/memory.py  # Хранение данных в оперативной памяти

docs/
  architecture.md         # Описание архитектуры, сценариев и ограничений
  swagger-checklist.md    # Инструкция по ручному тестированию API

tests/                    # Каталог для будущих регрессионных тестов
