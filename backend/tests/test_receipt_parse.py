from services.receipt import _parse_items_json


def test_parse_items_json_strips_markdown_fence():
    text = '```json\n["rockmelon large half", "brown onions 1kg"]\n```'
    assert _parse_items_json(text) == ["rockmelon large half", "brown onions 1kg"]


def test_parse_items_json_plain_array():
    assert _parse_items_json('["milk", "bread"]') == ["milk", "bread"]


def test_parse_items_json_apostrophe_in_item_name():
    text = '["S&B Curry Mix Golden Mild 92g", "Elmer\'s School Glue 225ml"]'
    assert _parse_items_json(text) == [
        "S&B Curry Mix Golden Mild 92g",
        "Elmer's School Glue 225ml",
    ]


def test_parse_items_json_smart_quotes():
    text = '[\u201crockmelon large half\u201d, \u201cbrown onions 1kg\u201d]'
    assert _parse_items_json(text) == ["rockmelon large half", "brown onions 1kg"]
