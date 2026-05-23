"""
Encode tests/fixtures/test_receipt.jpg to receipt_request.json for curl testing.

Run from backend/:  python scripts/encode_receipt_fixture.py
"""
import base64
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
FIXTURE_IMAGE = BACKEND_DIR / "tests" / "fixtures" / "test_receipt.jpg"
OUTPUT_JSON = BACKEND_DIR / "tests" / "fixtures" / "receipt_request.json"


def main() -> int:
    if not FIXTURE_IMAGE.is_file():
        print(f"Missing fixture: {FIXTURE_IMAGE}", file=sys.stderr)
        print("Add your test receipt as tests/fixtures/test_receipt.jpg", file=sys.stderr)
        return 1

    raw = FIXTURE_IMAGE.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    payload = {"image": encoded}
    OUTPUT_JSON.write_text(json.dumps(payload), encoding="utf-8")

    size_mb = len(encoded) / (1024 * 1024)
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Base64 size: {size_mb:.2f} MB")
    if size_mb > 1:
        print(
            "Warning: payloads over ~1 MB often fail in Swagger UI ('Failed to fetch'). "
            "Use curl or scripts/test_receipt.py instead.",
            file=sys.stderr,
        )
    print("\ncurl example:")
    print(
        f'curl -X POST http://localhost:8000/api/receipt '
        f'-H "Content-Type: application/json" '
        f'-d @{OUTPUT_JSON.relative_to(BACKEND_DIR).as_posix()}'
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
