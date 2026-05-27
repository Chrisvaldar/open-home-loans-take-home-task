"""
Test receipt extraction against tests/fixtures/test_receipt.jpg.

Run from backend/ (with .env loaded):
  python scripts/test_receipt.py

Optional — hit the running API instead of calling Gemini directly:
  python scripts/test_receipt.py --http
"""
import argparse
import base64
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
FIXTURE_IMAGE = BACKEND_DIR / "tests" / "fixtures" / "test_receipt.jpg"

load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(BACKEND_DIR))


def main() -> int:
    parser = argparse.ArgumentParser(description="Test receipt item extraction")
    parser.add_argument(
        "--http",
        action="store_true",
        help="POST to http://localhost:8000/api/receipt instead of calling the service directly",
    )
    args = parser.parse_args()

    if not FIXTURE_IMAGE.is_file():
        print(f"Missing fixture: {FIXTURE_IMAGE}", file=sys.stderr)
        print("Add your test receipt as tests/fixtures/test_receipt.jpg", file=sys.stderr)
        return 1

    encoded = base64.b64encode(FIXTURE_IMAGE.read_bytes()).decode("ascii")

    if args.http:
        try:
            import requests
        except ImportError:
            print("Install requests: pip install requests", file=sys.stderr)
            return 1
        response = requests.post(
            "http://localhost:8000/api/receipt",
            json={"image": encoded, "mime_type": "image/jpeg"},
            timeout=120,
        )
        response.raise_for_status()
        items = response.json().get("items", [])
    else:
        from services.receipt import extract_items_from_receipt

        items = extract_items_from_receipt(encoded, "image/jpeg")

    print(json.dumps(items, indent=2))
    print(f"\n{len(items)} item(s) extracted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
