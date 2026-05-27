from services.receipt import _parse_items_json


def test_parse_items_json_strips_markdown_fence():
    text = '```json\n["rockmelon large half", "brown onions 1kg"]\n```'
    assert _parse_items_json(text) == ["rockmelon large half", "brown onions 1kg"]


def test_parse_items_json_plain_array():
    assert _parse_items_json('["milk", "bread"]') == ["milk", "bread"]
