import base64
import json
import os
import re

from google import genai
from google.genai import types

RECEIPT_MODEL = "gemini-2.5-flash"

PROMPT = """Extract grocery items from this receipt. Return a JSON array of search-friendly product names. Follow these rules:

Remove store names, weights from item names (e.g. WOOLWORTHS, COLES prefix)
For produce/fresh items, convert receipt abbreviations to natural search terms: ONION BROWN 1KG → brown onions, CABBAGE GRN HALF → green cabbage half, TOMATOES PERKG → gourmet tomatoes, MELON ROCKMELON → rockmelon
For branded items, keep brand name and size: MCCAINS FROZEN PEAS 500G → McCain frozen peas 500g
Remove quantity/weight suffixes that are per-kg prices (PERKG, NET @)
Include all food and grocery lines; skip non-product lines like subtotals and payment details
Return only the JSON array, no markdown, no backticks"""


def _normalize_base64(image_base64: str) -> str:
    """Strip whitespace and data-URL prefix if present."""
    value = image_base64.strip()
    if value.startswith("data:") and "," in value:
        value = value.split(",", 1)[1]
    return value


def _normalize_mime_type(mime_type: str) -> str:
    """Normalize browser MIME aliases to values Gemini accepts."""
    value = mime_type.strip().lower()
    if value == "image/jpg":
        return "image/jpeg"
    if value == "image/heif":
        return "image/heic"
    return value or "image/jpeg"


def _parse_items_json(text: str) -> list[str]:
    """Parse Gemini output into a list of item strings."""
    value = text.strip()
    if not value:
        return []

    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?\s*", "", value, flags=re.IGNORECASE)
        value = re.sub(r"\s*```$", "", value).strip()

    try:
        items = json.loads(value)
        if isinstance(items, list):
            return [str(item).strip() for item in items if str(item).strip()]
    except json.JSONDecodeError:
        array_match = re.search(r"\[[\s\S]*\]", value)
        if array_match:
            items = json.loads(array_match.group())
            if isinstance(items, list):
                return [str(item).strip() for item in items if str(item).strip()]

    return []


def extract_items_from_receipt(
    image_base64: str, mime_type: str = "image/jpeg"
) -> list[str]:
    """Extract grocery item names from a receipt image via Gemini vision."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not image_base64:
        return []

    try:
        image_data = base64.b64decode(_normalize_base64(image_base64))

        with genai.Client(api_key=api_key) as client:
            response = client.models.generate_content(
                model=RECEIPT_MODEL,
                contents=[
                    PROMPT,
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type=_normalize_mime_type(mime_type),
                    ),
                ],
            )

        text = (response.text or "").strip()
        print(f"[receipt] Gemini raw response={text!r}")
        items = _parse_items_json(text)
        print(f"[receipt] parsed {len(items)} item(s): {items}")
        return items
    except Exception as exc:
        print(f"[receipt] extraction failed: {exc!r}")

    return []
