# API Smoke scope (Requests + Pytest)

Цель: быстрый прогон критичных публичных (без авторизации) API-ручек, чтобы понять “API жив / основные ответы корректны”.

База API задаётся переменной окружения:
- `API_BASE_URL` (пример: `https://api.prod.ads.ktsf.ru`)

## Набор тестов (9)

1) `test_cards_list_returns_200_and_has_results`
- Что проверяет: `/api/cards/?limit=12&offset=0` возвращает `200`, в JSON есть `results`, и он не пустой.
- Зачем: базовая выдача карточек работает.

2) `test_card_details_by_id_returns_200`
- Что проверяет: берём `id` первой карточки из списка и вызываем `/api/cards/{id}/`, получаем `200`, `id` совпадает.
- Зачем: карточка открывается по id.

3) `test_card_details_non_existent_returns_404`
- Что проверяет: `/api/cards/{fake_id}/` для заведомо большого id возвращает `404`.
- Зачем: корректная обработка “не найдено”.

4) `test_cards_pagination_limit_1_returns_single_item`
- Что проверяет: `/api/cards/?limit=1&offset=0` возвращает `200`, в `results` ровно 1 элемент.
- Зачем: базовая пагинация/лимит.

5) `test_card_has_basic_fields_in_list`
- Что проверяет: у первой карточки в `results` есть обязательные поля (минимум `id`), и есть человекочитаемое имя (`title` или `name`).
- Если у карточки присутствует цена (`price/current_price/start_price`) — она должна быть числом.
- Зачем: минимальная структура данных карточки валидна.

6) `test_categories_list_returns_200_and_not_empty`
- Что проверяет: `/api/categories/` возвращает `200`, JSON — список, он не пустой, у первого элемента есть `id`.
- Зачем: справочник категорий доступен.

7) `test_cards_offset_returns_different_item`
- Что проверяет: сравниваем id в `results[0]` для `offset=0` и `offset=1` (при `limit>=2`) — должны отличаться.
- Зачем: offset реально “сдвигает” выдачу.

8) `test_cards_list_count_consistency_if_present`
- Что проверяет: если в ответе списка есть поле `count`, то `count >= len(results)`.
- Зачем: согласованность метаданных пагинации.

9) `test_cards_limit_zero_returns_200_or_400_and_valid_json`
- Что проверяет: `/api/cards/?limit=0&offset=0` может вернуть `400` (валидация) или `200` (дефолтное поведение).
- Если `200` — проверяем, что JSON корректный и `results` — список.
- Зачем: фиксируем “граничный” кейс, не привязываясь к конкретной реализации.

## Запуск

### 1) Только API тесты (быстро)
```bash
API_BASE_URL="https://api.prod.ads.ktsf.ru" pytest -q tests/api -v

2) API тесты + Allure-результаты

API_BASE_URL="https://api.prod.ads.ktsf.ru" pytest -q tests/api --alluredir=allure-results

3) Открыть Allure (порт 4040)

allure generate allure-results -o allure-report --clean
allure open allure-report --host 0.0.0.0 --port 4040

Если браузер не открылся автоматически:

открой вручную http://localhost:4040/

или в VS Code → PORTS → 4040 → “Open in Browser”.

Примечания

Тесты intentionally без авторизации: только публичные ручки.

Для “плавающих” полей используем мягкие проверки (например, title или name, цена — если присутствует).