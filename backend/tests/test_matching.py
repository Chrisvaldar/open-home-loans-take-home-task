import pytest

from services.matching import (
    detect_search_type,
    expand_staple_query,
    filter_comparable_items,
    is_excluded_compare_item,
    is_staple_query,
    normalize_receipt_search_query,
    normalise_unit_price,
    pick_best_match,
    store_staple_search_term,
)


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


def test_generic_single_word_rejects_brand_only_match():
    results = [
        {
            "name": "Inspired Mud Cake",
            "brand": "Fairy Bread",
            "price": 7.10,
            "size": "600g",
            "on_special": False,
        },
        {
            "name": "White Bread",
            "brand": "coles",
            "price": 2.00,
            "size": "700g",
            "on_special": False,
        },
    ]

    match = pick_best_match("bread", results, "generic")
    assert match is not None
    assert match["name"] == "White Bread"


def test_generic_single_word_returns_none_when_name_has_no_query_word():
    results = [
        {
            "name": "Inspired Mud Cake",
            "brand": "Fairy Bread",
            "price": 7.10,
            "size": "600g",
            "on_special": False,
        },
    ]

    assert pick_best_match("bread", results, "generic") is None


def test_branded_still_uses_brand_field_for_scoring():
    results = [
        {
            "name": "Full Cream Milk 2L",
            "brand": "a2",
            "price": 5.50,
            "size": "2L",
            "on_special": False,
        },
    ]

    match = pick_best_match("a2 milk 2L", results, "branded")
    assert match is not None
    assert match["brand"] == "a2"


def test_expand_staple_query_substitutes_known_staples():
    assert expand_staple_query("milk") == "full cream milk 2L"
    assert expand_staple_query("bread") == "white sandwich bread loaf"
    assert expand_staple_query("  Milk  ") == "full cream milk 2L"


def test_store_staple_search_term_prefixes_store_name():
    assert (
        store_staple_search_term("full cream milk 2L", "woolworths")
        == "woolworths full cream milk 2L"
    )
    assert (
        store_staple_search_term("full cream milk 2L", "coles")
        == "coles full cream milk 2L"
    )


def test_is_staple_query():
    assert is_staple_query("milk") is True
    assert is_staple_query("a2 milk 2L") is False


def test_expand_staple_query_leaves_unknown_queries_unchanged():
    assert expand_staple_query("a2 milk 2L") == "a2 milk 2L"
    assert expand_staple_query("turkish bread") == "turkish bread"


def test_generic_uses_search_term_for_expanded_staples():
    results = [
        {
            "name": "Woolworths White Sandwich Loaf 650g",
            "brand": "Woolworths",
            "price": 3.20,
            "size": "650g",
            "on_special": False,
        },
    ]

    match = pick_best_match(
        "bread",
        results,
        "generic",
        search_term="white sandwich bread loaf",
    )
    assert match is not None
    assert "Woolworths" in match["name"]


def test_generic_prefers_cheapest_homebrand():
    results = [
        {
            "name": "a2 Milk Full Cream Milk",
            "brand": "a2 Milk",
            "price": 6.90,
            "size": "2L",
            "on_special": False,
        },
        {
            "name": "Woolworths Full Cream Milk",
            "brand": "Woolworths",
            "price": 2.50,
            "size": "2L",
            "on_special": False,
        },
        {
            "name": "Coles Full Cream Milk",
            "brand": "Coles",
            "price": 2.80,
            "size": "2L",
            "on_special": False,
        },
    ]

    match = pick_best_match(
        "milk",
        results,
        "generic",
        search_term="full cream milk 2L",
    )
    assert match is not None
    assert match["brand"] == "Woolworths"
    assert match["price"] == 2.50


def test_generic_picks_cheapest_when_no_homebrand():
    results = [
        {
            "name": "White Sandwich Bread",
            "brand": "Mighty Soft",
            "price": 4.00,
            "size": "700g",
            "on_special": False,
        },
        {
            "name": "White Sandwich Bread Loaf",
            "brand": "Bakers Life",
            "price": 3.50,
            "size": "650g",
            "on_special": False,
        },
    ]

    match = pick_best_match(
        "bread",
        results,
        "generic",
        search_term="white sandwich bread loaf",
    )
    assert match is not None
    assert match["price"] == 3.50


def test_normalize_receipt_search_query_strips_store_prefix_and_size():
    assert normalize_receipt_search_query("COLES BEEF 4 STAR LE 500GRAM") == (
        "beef 4 star lean"
    )


def test_normalize_receipt_search_query_fixes_ocr_noise():
    assert normalize_receipt_search_query("MCCAINS FROZEN:PEAS 500GRAM") == (
        "mccains frozen peas"
    )
    assert normalize_receipt_search_query("SOMAT EXCELLENCE CAP 74PACK") == (
        "somat excellence tablets"
    )


def test_is_excluded_compare_item_reusable_bags():
    assert is_excluded_compare_item("reusable shopping bag")
    assert is_excluded_compare_item("COLES REUSABLE BAG")
    assert is_excluded_compare_item("Woolworths bag for good")
    assert is_excluded_compare_item("carrier bag")
    assert not is_excluded_compare_item("brown onions 1kg")
    assert not is_excluded_compare_item("bagels")


def test_filter_comparable_items():
    assert filter_comparable_items(
        ["milk", "reusable bag", "bread", "eco bag"]
    ) == ["milk", "bread"]
