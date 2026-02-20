# KP Production Tests

Автоматизированные UI и API smoke-тесты для проекта  
https://kp.ktsf.ru/

## О проекте

Данный smoke-набор был разработан после доработок фронтенда и бэкенда
для быстрой проверки базовой работоспособности системы 20.02.2026.

Цель — дать команде (frontend и backend разработчикам) простой инструмент,
который позволяет быстро убедиться, что:

- сайт открывается и основные UI-сценарии работают
- публичные API-ручки отвечают корректно
- после релиза или правок ничего критичного не "сломалось"


Проект создан и используется как внутренний
smoke-инструмент для команды.


---

## 1. Клонирование проекта

git clone https://github.com/imdig1825/kp-production-tests.git
cd kp-production-tests

---

## 2. Среда разработки

Проект разрабатывался и запускался в следующей среде:

- ОС: Windows 11 + WSL (Ubuntu)
- Python: 3.10.x
- Pytest
- Playwright
- Requests
- Allure

Рекомендуется использовать виртуальное окружение.

---

## 3. Установка зависимостей

Создать виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
playwright install
```

---

## 4. Структура проекта

```
tests/
  ui/
    test_smoke_ui.py
    SMOKE_SCOPE.md
  api/
    test_smoke_api.py
    API_SCOPE.md

run_tests.sh
requirements.txt
pytest.ini
```

---

## 5. UI Smoke Tests

UI тесты проверяют критичные пользовательские сценарии без авторизации.

База:
https://kp.ktsf.ru/

Подробное описание набора:
```
tests/ui/SMOKE_SCOPE.md
```

Запуск только UI:

```bash
pytest -q tests/ui
```

---

## 6. API Smoke Tests

API тесты проверяют публичные ручки без авторизации.

База задаётся через переменную окружения:

```bash
API_BASE_URL="https://api.prod.ads.ktsf.ru"
```

Подробное описание набора:
```
tests/api/API_SCOPE.md
```

Запуск только API:

```bash
API_BASE_URL="https://api.prod.ads.ktsf.ru" pytest -q tests/api -v
```

---

## 7. Полный запуск (UI + API) + Allure

```bash
API_BASE_URL="https://api.prod.ads.ktsf.ru" ./run_tests.sh
```

После выполнения:

- генерируется Allure-отчёт
- сервер поднимается на порту 4040

Открыть отчёт:
http://localhost:4040/

Если не открылось автоматически:
VS Code → PORTS → 4040 → Open in Browser

---

## 8. Allure отчёт

Используется Allure для визуализации результатов тестирования.

Генерация вручную:

```bash
allure generate allure-results -o allure-report --clean
allure open allure-report --port 4040
```

---

## 9. Принципы

- Smoke-подход: быстрый прогон критичных сценариев
- UI — проверка доступности и ключевых действий
- API — проверка статусов и базовой структуры ответа
- Используются мягкие проверки для устойчивости к несущественным изменениям

---

## 10. Текущее покрытие

- UI: 7 тестов
- API: 9 тестов
- Общий smoke-набор: 16 тестов
