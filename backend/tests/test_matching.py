import pytest

from services.matching import detect_search_type, normalise_unit_price, pick_best_match


def test_detect_search_type_branded():
    assert detect_search_type("a2 milk") == "branded"


def test_detect_search_type_generic():
    assert detect_search_type("full cream milk") == "generic"


def test_normalise_unit_price_2l():
    price = 5.6
    result = normalise_unit_price(price, "2L")
    assert result is not None
    unit_price, unit_label = result
    assert unit_label == "per 100ml"
    assert unit_price == pytest.approx(price / 2000 * 100)


def test_normalise_unit_price_unparseable():
    assert normalise_unit_price(4.0, "each") is None
