import os
import requests


def test_cards_list_returns_200_and_has_results():
    base_url = os.getenv("API_BASE_URL")
    assert base_url, "API_BASE_URL не задан"

    url = f"{base_url.rstrip('/')}/api/cards/?limit=12&offset=0"
    response = requests.get(url, timeout=10)

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) > 0

def test_card_details_by_id_returns_200():
    base_url = os.getenv("API_BASE_URL")
    assert base_url, "API_BASE_URL не задан"

    list_url = f"{base_url.rstrip('/')}/api/cards/?limit=12&offset=0"
    list_response = requests.get(list_url, timeout=10)
    assert list_response.status_code == 200

    data = list_response.json()
    card_id = data["results"][0]["id"]

    details_url = f"{base_url.rstrip('/')}/api/cards/{card_id}/"
    details_response = requests.get(details_url, timeout=10)

    assert details_response.status_code == 200

    details_data = details_response.json()
    assert isinstance(details_data, dict)
    assert details_data["id"] == card_id

def test_card_details_non_existent_returns_404():
    base_url = os.getenv("API_BASE_URL")
    assert base_url, "API_BASE_URL не задан"

    fake_id = 999999999  # заведомо большой
    url = f"{base_url.rstrip('/')}/api/cards/{fake_id}/"
    response = requests.get(url, timeout=10)

    assert response.status_code == 404

def test_cards_pagination_limit_1_returns_single_item():
    base_url = os.getenv("API_BASE_URL")
    assert base_url, "API_BASE_URL не задан"

    url = f"{base_url.rstrip('/')}/api/cards/?limit=1&offset=0"
    response = requests.get(url, timeout=10)

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1


def test_card_has_basic_fields_in_list():
    base_url = os.getenv("API_BASE_URL")
    assert base_url, "API_BASE_URL не задан"

    url = f"{base_url.rstrip('/')}/api/cards/?limit=12&offset=0"
    response = requests.get(url, timeout=10)

    assert response.status_code == 200

    data = response.json()
    first = data["results"][0]
    assert isinstance(first, dict)

    # обязательное: id
    assert "id" in first
    assert isinstance(first["id"], int)

    # “человеческое имя” карточки: у разных API может быть title/name
    title = first.get("title") or first.get("name")
    assert title is not None, f"Нет ни title, ни name. keys={list(first.keys())}"
    assert isinstance(title, str)
    assert title.strip() != ""

    # цена может быть в разных полях — проверяем мягко, если есть
    price = first.get("price") or first.get("current_price") or first.get("start_price")
    if price is not None:
        assert isinstance(price, (int, float)), f"Цена должна быть числом, получили {type(price)}"

def test_categories_list_returns_200_and_not_empty():
    base_url = os.getenv("API_BASE_URL")
    assert base_url, "API_BASE_URL не задан"

    url = f"{base_url.rstrip('/')}/api/categories/"
    response = requests.get(url, timeout=10)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    first = data[0]
    assert isinstance(first, dict)
    assert "id" in first
    assert isinstance(first["id"], int)

def test_cards_offset_returns_different_item():
    base_url = os.getenv("API_BASE_URL")
    assert base_url, "API_BASE_URL не задан"

    url_0 = f"{base_url.rstrip('/')}/api/cards/?limit=1&offset=0"
    url_1 = f"{base_url.rstrip('/')}/api/cards/?limit=1&offset=1"

    r0 = requests.get(url_0, timeout=10)
    r1 = requests.get(url_1, timeout=10)

    assert r0.status_code == 200
    assert r1.status_code == 200

    id_0 = r0.json()["results"][0]["id"]
    id_1 = r1.json()["results"][0]["id"]

    assert id_0 != id_1


def test_cards_list_count_consistency_if_present():
    base_url = os.getenv("API_BASE_URL")
    assert base_url, "API_BASE_URL не задан"

    url = f"{base_url.rstrip('/')}/api/cards/?limit=5&offset=0"
    response = requests.get(url, timeout=10)

    assert response.status_code == 200
    data = response.json()

    # если API отдает count — проверяем, что он не меньше размера results
    if "count" in data:
        assert data["count"] >= len(data["results"])


def test_cards_limit_zero_returns_200_or_400_and_valid_json():
    base_url = os.getenv("API_BASE_URL")
    assert base_url, "API_BASE_URL не задан"

    url = f"{base_url.rstrip('/')}/api/cards/?limit=0&offset=0"
    response = requests.get(url, timeout=10)

    # API может трактовать limit=0 по-разному: либо 400, либо 200 с дефолтным лимитом
    assert response.status_code in (200, 400)

    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

    base_url = os.getenv("API_BASE_URL")
    assert base_url, "API_BASE_URL не задан"

    url = f"{base_url.rstrip('/')}/api/cards/?limit=0&offset=0"
    response = requests.get(url, timeout=10)

    assert response.status_code in (200, 400)

    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        
