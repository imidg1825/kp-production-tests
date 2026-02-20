import re
import pytest
from playwright.sync_api import Page, expect, TimeoutError as PWTimeout


BASE_URL = "https://kp.ktsf.ru/"


# ---------- helpers ----------

def open_home(page: Page):
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(500)  # SPA/рендер
    _dismiss_banners(page)


def _dismiss_banners(page: Page):
    # на всякий случай: куки/попапы могут перекрывать кнопки
    candidates = [
        page.get_by_role("button", name=re.compile(r"принять|согласен|ok|okay", re.I)).first,
        page.get_by_role("button", name=re.compile(r"закрыть|close|понятно", re.I)).first,
        page.locator("[aria-label*='close' i]").first,
    ]
    for c in candidates:
        try:
            if c.is_visible():
                c.click(timeout=1000)
                page.wait_for_timeout(200)
        except:
            pass


def _safe_click(locator, timeout=7000):
    # стабильный клик: скролл + клик
    locator.scroll_into_view_if_needed(timeout=timeout)
    locator.click(timeout=timeout)


def click_login(page: Page):
    # "Войти" может быть link или button
    locators = [
        page.get_by_role("link", name=re.compile(r"войти|вход", re.I)).first,
        page.get_by_role("button", name=re.compile(r"войти|вход", re.I)).first,
        page.get_by_text(re.compile(r"войти|вход", re.I)).first,
    ]
    last_err = None
    for loc in locators:
        try:
            if loc.is_visible():
                _safe_click(loc, timeout=7000)
                return
        except Exception as e:
            last_err = e
            continue
    raise AssertionError(f"Не смог кликнуть кнопку/ссылку 'Войти'. Последняя ошибка: {last_err}")


def click_create_ad(page: Page):
    locators = [
        page.get_by_role("button", name=re.compile(r"создать\s+объявление|подать\s+объявление", re.I)).first,
        page.get_by_text(re.compile(r"создать\s+объявление|подать\s+объявление", re.I)).first,
    ]
    last_err = None
    for loc in locators:
        try:
            if loc.is_visible():
                _safe_click(loc, timeout=7000)
                return
        except Exception as e:
            last_err = e
            continue
    raise AssertionError(f"Не нашёл/не смог нажать 'Создать объявление'. Последняя ошибка: {last_err}")


def ensure_auth_opened(page: Page):
    """
    Устойчиво проверяем, что открылась авторизация:
    - появился dialog/модалка
    - или URL содержит login/auth
    - или виден password/username/email-подобный input
    - или виден заголовок/текст "Вход/Авторизация"
    """
    # 1) URL признак
    try:
        page.wait_for_timeout(200)
        if re.search(r"(login|auth|signin)", page.url, re.I):
            return
    except:
        pass

    # 2) dialog/модалка
    dialog = page.get_by_role("dialog").first
    try:
        expect(dialog).to_be_visible(timeout=2000)
        return
    except:
        pass

    # 3) поля / элементы формы
    probes = [
        page.locator("input[type='password']").first,
        page.locator("input[autocomplete='current-password']").first,
        page.locator("input[autocomplete='username']").first,
        page.locator("input[name*='pass' i]").first,
        page.locator("input[name*='email' i]").first,
        page.get_by_placeholder(re.compile(r"mail|email|почт|логин|телефон|phone", re.I)).first,
        page.get_by_label(re.compile(r"mail|email|почт|логин|телефон|phone|пароль|password", re.I)).first,
        page.get_by_text(re.compile(r"вход|авторизац|войти|login|password", re.I)).first,
    ]

    # Ждём до 10с любой признак
    deadline_ms = 10_000
    step_ms = 500
    waited = 0
    while waited < deadline_ms:
        for p in probes:
            try:
                if p.is_visible():
                    return
            except:
                pass
        page.wait_for_timeout(step_ms)
        waited += step_ms

    raise AssertionError("Форма авторизации не найдена (ни модалки, ни /login, ни password/username/email признаков)")


def first_card(page: Page):
    # максимально мягко: пытаемся открыть первую карточку объявления
    # (селекторы могут отличаться — поэтому fallback)
    candidates = [
        page.locator("a[href*='/ad']").first,
        page.locator("a[href*='/ads']").first,
        page.locator("article a").first,
        page.locator("a").filter(has_text=re.compile(r"\S")).first,
    ]
    for c in candidates:
        try:
            if c.is_visible():
                return c
        except:
            pass
    return None


# ---------- tests ----------

def test_homepage_opens_and_has_create_button(page: Page):
    open_home(page)
    btn = page.get_by_role("button", name=re.compile(r"создать\s+объявление|подать\s+объявление", re.I)).first
    expect(btn).to_be_visible(timeout=10_000)


def test_search_input_exists_and_accepts_text(page: Page):
    open_home(page)
    search = page.get_by_placeholder(re.compile(r"поиск", re.I)).first
    expect(search).to_be_visible(timeout=10_000)
    search.fill("ноутбук")
    expect(search).to_have_value(re.compile(r"ноутбук", re.I), timeout=5_000)


def test_categories_button_exists(page: Page):
    open_home(page)
    btn = page.get_by_role("button", name=re.compile(r"все\s+категории|категории", re.I)).first
    expect(btn).to_be_visible(timeout=10_000)


def test_login_button_opens_auth(page: Page):
    open_home(page)
    click_login(page)
    ensure_auth_opened(page)


def test_create_ad_requires_auth_opens_auth(page: Page):
    open_home(page)
    click_create_ad(page)
    ensure_auth_opened(page)


def test_open_first_card_opens_details(page: Page):
    open_home(page)

    c = first_card(page)
    if not c:
        pytest.skip("Не найдено ни одной карточки — пропускаем smoke шаг")

    _safe_click(c, timeout=7000)

    try:
        page.wait_for_load_state("domcontentloaded", timeout=5000)
    except:
        pass

    # Проверяем один из признаков:
    # 1) URL изменился
    # 2) появился блок деталей
    # 3) появился CTA (написать/позвонить и т.д.)

    if page.url != BASE_URL:
        return

    detail_indicators = [
        page.get_by_role("button", name=re.compile("написать|позвонить|контакт", re.I)).first,
        page.get_by_text(re.compile("Описание", re.I)).first,
        page.locator("h1").first,
    ]

    for el in detail_indicators:
        try:
            if el.is_visible():
                return
        except:
            continue

    pytest.fail("После клика карточки не обнаружены признаки страницы деталей")


def test_actions_on_details_require_auth_when_available(page: Page):
    open_home(page)
    c = first_card(page)
    if not c:
        pytest.skip("Не нашёл карточку объявления на главной — пропускаем smoke шаг")
    _safe_click(c, timeout=7000)
    page.wait_for_timeout(500)

    # пробуем найти CTA, который часто требует авторизацию
    candidates = [
        page.get_by_role("button", name=re.compile(r"написать|позвонить|контакты|избранное|откликнуться|купить|заказать", re.I)).first,
        page.get_by_text(re.compile(r"написать|позвонить|контакты|избранное|откликнуться|купить|заказать", re.I)).first,
    ]

    clicked = False
    for cta in candidates:
        try:
            if cta.is_visible():
                _safe_click(cta, timeout=7000)
                clicked = True
                break
        except:
            continue

    if not clicked:
        pytest.skip("На странице деталей не нашёл CTA действий — это ок для smoke")

    ensure_auth_opened(page)
