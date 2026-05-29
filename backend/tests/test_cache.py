import time

import pytest

from services.cache import clear_cache, get_cached_search, set_cached_search


@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache()
    yield
    clear_cache()


def test_cache_miss_returns_none():
    assert get_cached_search("woolworths", "milk", 3) is None


def test_cache_hit_returns_stored_results():
    results = [{"name": "Milk 2L", "price": 2.5}]
    set_cached_search("woolworths", "milk", 3, results)

    cached = get_cached_search("woolworths", "milk", 3)
    assert cached == results
    assert cached is not results


def test_cache_normalises_query_whitespace_and_case():
    results = [{"name": "Milk 2L", "price": 2.5}]
    set_cached_search("coles", "  Milk  ", 3, results)

    assert get_cached_search("coles", "milk", 3) == results


def test_cache_expires_after_ttl(monkeypatch):
    monkeypatch.setenv("SEARCH_CACHE_TTL_SECONDS", "1")
    set_cached_search("woolworths", "bread", 3, [{"name": "Bread"}])

    assert get_cached_search("woolworths", "bread", 3) is not None
    time.sleep(1.1)
    assert get_cached_search("woolworths", "bread", 3) is None


def test_cache_key_includes_store_and_page_size():
    set_cached_search("woolworths", "milk", 3, [{"name": "Woolies Milk"}])
    set_cached_search("coles", "milk", 3, [{"name": "Coles Milk"}])
    set_cached_search("woolworths", "milk", 10, [{"name": "Woolies Milk 10"}])

    assert get_cached_search("woolworths", "milk", 3)[0]["name"] == "Woolies Milk"
    assert get_cached_search("coles", "milk", 3)[0]["name"] == "Coles Milk"
    assert get_cached_search("woolworths", "milk", 10)[0]["name"] == "Woolies Milk 10"
