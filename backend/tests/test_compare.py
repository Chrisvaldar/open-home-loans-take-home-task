import pytest
from unittest.mock import patch
from services.compare import compare_basket

# Controlled mock data — we decide exactly what each store returns
MOCK_WOOLWORTHS_CHEAP_MILK = {
    "name": "Milk 2L",
    "brand": "woolworths",
    "price": 2.50,
    "size": "2L",
    "on_special": False,
}

MOCK_COLES_EXPENSIVE_MILK = {
    "name": "Milk 2L",
    "brand": "coles",
    "price": 3.20,
    "size": "2L",
    "on_special": False,
}

MOCK_COLES_CHEAP_BREAD = {
    "name": "White Bread",
    "brand": "coles",
    "price": 2.00,
    "size": "700g",
    "on_special": False,
}

MOCK_WOOLWORTHS_EXPENSIVE_BREAD = {
    "name": "White Bread",
    "brand": "woolworths",
    "price": 2.80,
    "size": "700g",
    "on_special": False,
}

MOCK_A2_WOOLWORTHS = {
    "name": "a2 Full Cream Milk 2L",
    "brand": "a2",
    "price": 5.50,
    "size": "2L",
    "on_special": False,
}

MOCK_A2_COLES = {
    "name": "a2 Full Cream Milk 1L",
    "brand": "a2",
    "price": 3.20,
    "size": "1L",
    "on_special": False,
}


# Helper — build a side_effect function for search_item mocks
def make_search_side_effect(*results):
    """Returns a function that returns results[0] as a list, ignoring the query."""
    def side_effect(query, page_size=3):
        return list(results)
    return side_effect


@patch("services.compare.search_woolworths")
@patch("services.compare.search_coles")
def test_woolworths_wins_on_total_price(mock_coles, mock_woolworths):
    mock_woolworths.side_effect = make_search_side_effect(MOCK_WOOLWORTHS_CHEAP_MILK)
    mock_coles.side_effect = make_search_side_effect(MOCK_COLES_EXPENSIVE_MILK)

    result = compare_basket(["milk"])
    assert result["winner"] == "woolworths"
    assert result["total_woolworths"] < result["total_coles"]
    assert result["savings"] > 0


@patch("services.compare.search_woolworths")
@patch("services.compare.search_coles")
def test_coles_wins_on_total_price(mock_coles, mock_woolworths):
    mock_woolworths.side_effect = make_search_side_effect(MOCK_WOOLWORTHS_EXPENSIVE_BREAD)
    mock_coles.side_effect = make_search_side_effect(MOCK_COLES_CHEAP_BREAD)

    result = compare_basket(["bread"])
    assert result["winner"] == "coles"
    assert result["total_coles"] < result["total_woolworths"]
    assert result["savings"] > 0


@patch("services.compare.search_woolworths")
@patch("services.compare.search_coles")
def test_tie_within_fifty_cents(mock_coles, mock_woolworths):
    same_price = {**MOCK_WOOLWORTHS_CHEAP_MILK, "price": 2.80}
    mock_woolworths.side_effect = make_search_side_effect(same_price)
    mock_coles.side_effect = make_search_side_effect(
        {**MOCK_COLES_EXPENSIVE_MILK, "price": 2.80}
    )

    result = compare_basket(["milk"])
    assert result["winner"] == "tie"
    assert abs(result["total_woolworths"] - result["total_coles"]) <= 0.50


def test_empty_list_returns_valid_empty_breakdown():
    result = compare_basket([])
    assert result["breakdown"] == []
    assert result["total_woolworths"] == 0.0
    assert result["total_coles"] == 0.0
    assert result["savings"] == 0.0
    assert result["annualised_savings"] == 0.0


@patch("services.compare.search_woolworths")
@patch("services.compare.search_coles")
def test_brand_mismatch_generic_note(mock_coles, mock_woolworths):
    # Both stores return different brands for a generic search
    woolies_result = {
        "name": "Full Cream Milk 2L",
        "brand": "woolworths",
        "price": 2.50,
        "size": "2L",
        "on_special": False,
    }
    coles_result = {
        "name": "Full Cream Milk 2L",
        "brand": "coles",
        "price": 3.20,
        "size": "2L",
        "on_special": False,
    }
    mock_woolworths.side_effect = make_search_side_effect(woolies_result)
    mock_coles.side_effect = make_search_side_effect(coles_result)

    result = compare_basket(["full cream milk"])
    item = result["breakdown"][0]
    assert item["match_type"] == "generic"
    assert item["note"] is not None
    assert "brand" in item["note"].lower()


@patch("services.compare.search_woolworths")
@patch("services.compare.search_coles")
def test_one_store_missing_brand_no_comparison(mock_coles, mock_woolworths):
    # Woolworths has a2, Coles returns no brand match
    mock_woolworths.side_effect = make_search_side_effect(MOCK_A2_WOOLWORTHS)
    mock_coles.side_effect = make_search_side_effect(
        {**MOCK_COLES_EXPENSIVE_MILK, "brand": "coles"}  # not a2
    )

    result = compare_basket(["a2 milk 2L"])
    item = result["breakdown"][0]
    assert item["winner"] == "no_comparison"
    assert item["coles"] is None


@patch("services.compare.search_woolworths")
@patch("services.compare.search_coles")
def test_unit_price_normalisation_different_sizes(mock_coles, mock_woolworths):
    # Woolworths has 2L, Coles has 1L — must normalise to per 100ml
    mock_woolworths.side_effect = make_search_side_effect(MOCK_A2_WOOLWORTHS)
    mock_coles.side_effect = make_search_side_effect(MOCK_A2_COLES)

    result = compare_basket(["a2 milk"])
    item = result["breakdown"][0]
    assert item["woolworths"]["unit"] == "per 100ml"
    assert item["coles"]["unit"] == "per 100ml"
    assert item["woolworths"]["unit_price"] is not None
    assert item["coles"]["unit_price"] is not None


@patch("services.compare.search_woolworths")
@patch("services.compare.search_coles")
def test_low_confidence_match_returns_no_match(mock_coles, mock_woolworths):
    # Both stores return empty results for a nonsense query
    mock_woolworths.side_effect = make_search_side_effect()
    mock_coles.side_effect = make_search_side_effect()

    result = compare_basket(["xyznonexistentproduct123"])
    item = result["breakdown"][0]
    assert item["match_type"] == "no_match"


@patch("services.compare.rerank_with_groq")
@patch("services.compare.search_woolworths")
@patch("services.compare.search_coles")
def test_receipt_source_uses_groq_reranker(
    mock_coles, mock_woolworths, mock_rerank
):
    mock_woolworths.side_effect = make_search_side_effect(
        MOCK_WOOLWORTHS_CHEAP_MILK,
        {**MOCK_WOOLWORTHS_CHEAP_MILK, "name": "Wrong Product"},
    )
    mock_coles.side_effect = make_search_side_effect(MOCK_COLES_EXPENSIVE_MILK)
    mock_rerank.side_effect = lambda query, candidates: candidates[0]

    result = compare_basket(["SOMAT EXCELLENCE CAP 74PACK"], source="receipt")

    assert mock_rerank.call_count == 2
    item = result["breakdown"][0]
    assert item["woolworths"]["name"] == "Milk 2L"


@patch("services.compare.search_woolworths")
@patch("services.compare.search_coles")
def test_compare_basket_skips_reusable_bags(mock_coles, mock_woolworths):
    mock_woolworths.side_effect = make_search_side_effect(MOCK_WOOLWORTHS_CHEAP_MILK)
    mock_coles.side_effect = make_search_side_effect(MOCK_COLES_EXPENSIVE_MILK)

    result = compare_basket(["reusable shopping bag", "milk"])

    assert len(result["breakdown"]) == 1
    assert result["breakdown"][0]["item"] == "milk"
    assert mock_woolworths.call_count == 1
    assert mock_coles.call_count == 1