from services.woolworths import search_item as search_woolworths
from services.coles import search_item as search_coles

def compare_basket(items: list[str]) -> dict:
    """
    Compare a shopping list across Woolworths and Coles.

    TODO: Wire up woolworths/coles search, matching, and price comparison logic.
    """
    return {
        "winner": "tie",
        "total_woolworths": 0.0,
        "total_coles": 0.0,
        "savings": 0.0,
        "annualised_savings": 0.0,
        "breakdown": [],
    }
