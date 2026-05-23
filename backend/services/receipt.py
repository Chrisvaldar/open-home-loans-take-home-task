import json
import os

import anthropic

RECEIPT_MODEL = "claude-sonnet-4-20250514"


def extract_items_from_receipt(image_base64: str) -> list[str]:
    """Extract grocery item names from a receipt image via Claude vision."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or not image_base64:
        return []

    prompt = (
        "Extract grocery item names from this receipt image. "
        "Return as a JSON array of strings, brand names included, "
        "no prices, no quantities."
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=RECEIPT_MODEL,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        text = message.content[0].text.strip()
        items = json.loads(text)
        if isinstance(items, list):
            return [str(item) for item in items]
    except Exception:
        pass

    return []
