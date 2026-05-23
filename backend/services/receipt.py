import base64
import json
import os

from google import genai
from google.genai import types

RECEIPT_MODEL = "gemini-2.5-flash"

PROMPT = (
    "Extract grocery item names from this receipt image. "
    "Return ONLY a JSON array of strings, brand names included, "
    "no prices, no quantities. No markdown, no backticks, just the array."
)


def _normalize_base64(image_base64: str) -> str:
    """Strip whitespace and data-URL prefix if present."""
    value = image_base64.strip()
    if value.startswith("data:") and "," in value:
        value = value.split(",", 1)[1]
    return value


def extract_items_from_receipt(image_base64: str) -> list[str]:
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
                        mime_type="image/jpeg",
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
