from services.groq_reranker import is_produce_query


def test_is_produce_query_detects_produce():
    assert is_produce_query("brown onions 1kg")
    assert is_produce_query("green cabbage half")
    assert is_produce_query("rockmelon large half")
    assert is_produce_query("beef mince 500g")


def test_is_produce_query_rejects_non_produce():
    assert not is_produce_query("S&B Curry Mix Golden Mild 92g")
    assert not is_produce_query("Ant Rid Ant Baits 4 pack 6g")
