import base64
import json
import os

from google import genai
from google.genai import types

RECEIPT_MODEL = "gemini-2.5-flash"

PROMPT = (
    "Extract grocery item names from this receipt image. "
    "Include the product size or weight if it appears on the receipt "
    "(e.g. '700g', '2L', '100g', '8pk') as part of the item name string. "
    "Return ONLY a JSON array of strings, brand names included, "
    "no prices, no quantities as separate fields. "
    "No markdown, no backticks, just the array. "
    "Example output: [\"Helgas Traditional White Wraps 509g\", "
    "\"The Good Farmer Free Range Eggs 700g\"]"
)


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
        items = json.loads(text)
        if isinstance(items, list):
            return [str(item) for item in items]
    except Exception:
        pass

    return []
