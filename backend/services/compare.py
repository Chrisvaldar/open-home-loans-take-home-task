from services.woolworths import search_item as search_woolworths
from services.coles import search_item as search_coles
from services.matching import (
    detect_search_type,
    expand_staple_query,
    is_staple_query,
    pick_best_match,
    normalise_unit_price,
    store_staple_search_term,
)


def _build_store_result(match: dict | None) -> dict | None:
    """Convert a raw API result into the standardised store result shape."""
    if match is None:
        return None

    price = match.get("price") or 0.0
    size = match.get("size") or ""
    normalised = normalise_unit_price(price, size)

    return {
        "name": match.get("name") or "",
        "brand": match.get("brand") or "",
        "price": price,
        "size": size,
        "unit_price": normalised[0] if normalised else None,
        "unit": normalised[1] if normalised else None,
        "on_special": match.get("on_special") or False,
        "confidence": _confidence(match),
    }


def _confidence(match: dict) -> str:
    """Derive a confidence label from the match score if present, else 'medium'."""
    score = match.get("_score")
    if score is None:
        return "medium"
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def _item_winner(w_result: dict | None, c_result: dict | None) -> tuple[str, float]:
    """
    Determine the winner for a single item.
    Returns (winner, saving) where saving is always >= 0.
    Uses unit_price for comparison when both are available, else pack price.
    """
    if w_result is None and c_result is None:
        return "no_comparison", 0.0
    if w_result is None:
        return "no_comparison", 0.0
    if c_result is None:
        return "no_comparison", 0.0

    w_unit = w_result["unit_price"]
    c_unit = c_result["unit_price"]
    both_have_unit_price = w_unit is not None and c_unit is not None

    # Prefer unit price for winner when both available; else pack price
    if both_have_unit_price:
        w_compare = w_unit
        c_compare = c_unit
    else:
        w_compare = w_result["price"]
        c_compare = c_result["price"]

    diff = abs(w_compare - c_compare)

    # Tie threshold — within 2% of each other or less than 1 cent per 100ml/g
    if diff < 0.01 or (max(w_compare, c_compare) > 0 and diff / max(w_compare, c_compare) < 0.02):
        return "tie", 0.0

    if w_compare < c_compare:
        winner = "woolworths"
    else:
        winner = "coles"

    # Unit-price saving when both normalised; otherwise pack price difference
    if both_have_unit_price:
        saving = round(abs(w_unit - c_unit), 4)
    else:
        saving = round(abs(w_result["price"] - c_result["price"]), 2)

    return winner, saving


def _build_note(
    search_type: str,
    w_result: dict | None,
    c_result: dict | None,
    winner: str,
) -> str | None:
    """Generate a human-readable note about the comparison quality."""
    if winner == "no_comparison":
        if w_result is None and c_result is None:
            return "No match found at either store"
        if w_result is None:
            return "Not available at Woolworths"
        if c_result is None:
            return "Not available at Coles"

    if search_type == "generic" and w_result and c_result:
        w_brand = (w_result.get("brand") or "").lower()
        c_brand = (c_result.get("brand") or "").lower()
        if w_brand and c_brand and w_brand != c_brand:
            return "Different brands — comparing unit price where possible"

    if w_result and c_result:
        w_size = (w_result.get("size") or "").lower()
        c_size = (c_result.get("size") or "").lower()
        if w_size and c_size and w_size != c_size:
            return f"Different pack sizes ({w_result['size']} vs {c_result['size']}) — comparing per unit price"

    return None


def compare_basket(items: list[str]) -> dict:
    """Compare a shopping list across Woolworths and Coles."""
    if not items:
        return {
            "winner": "tie",
            "total_woolworths": 0.0,
            "total_coles": 0.0,
            "savings": 0.0,
            "annualised_savings": 0.0,
            "breakdown": [],
        }

    breakdown = []
    total_woolworths = 0.0
    total_coles = 0.0

    for item in items:
        search_type = detect_search_type(item)
        search_term = expand_staple_query(item)

        if search_type == "generic" and is_staple_query(item):
            w_raw = search_woolworths(
                store_staple_search_term(search_term, "woolworths")
            )
            c_raw = search_coles(store_staple_search_term(search_term, "coles"))
        else:
            w_raw = search_woolworths(search_term)
            c_raw = search_coles(search_term)

        # Pick best match from each store's results
        w_match = pick_best_match(item, w_raw, search_type, search_term=search_term)
        c_match = pick_best_match(item, c_raw, search_type, search_term=search_term)

        # No match at either store
        if w_match is None and c_match is None:
            breakdown.append({
                "item": item,
                "match_type": "no_match",
                "woolworths": None,
                "coles": None,
                "winner": "no_comparison",
                "saving": 0.0,
                "note": "No match found at either store",
            })
            continue

        # Build standardised result shapes
        w_result = _build_store_result(w_match)
        c_result = _build_store_result(c_match)

        # Determine match type
        if search_type == "branded":
            match_type = "branded"
        else:
            match_type = "generic"

        # Determine winner and saving for this item
        winner, saving = _item_winner(w_result, c_result)

        # Build note
        note = _build_note(search_type, w_result, c_result, winner)

        # Accumulate totals — only count items where both stores have a result
        if w_result and winner != "no_comparison":
            total_woolworths += w_result["price"]
        if c_result and winner != "no_comparison":
            total_coles += c_result["price"]

        breakdown.append({
            "item": item,
            "match_type": match_type,
            "woolworths": w_result,
            "coles": c_result,
            "winner": winner,
            "saving": saving,
            "note": note,
        })

    # Overall winner based on totals
    diff = total_woolworths - total_coles
    if abs(diff) <= 0.50:
        overall_winner = "tie"
        overall_savings = 0.0
    elif diff < 0:
        overall_winner = "woolworths"
        overall_savings = round(abs(diff), 2)
    else:
        overall_winner = "coles"
        overall_savings = round(abs(diff), 2)

    return {
        "winner": overall_winner,
        "total_woolworths": round(total_woolworths, 2),
        "total_coles": round(total_coles, 2),
        "savings": overall_savings,
        "annualised_savings": round(overall_savings * 52, 2),
        "breakdown": breakdown,
    }