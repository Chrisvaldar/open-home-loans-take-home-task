from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app
from services.rate_limit import clear_rate_limits

MOCK_MILK = {
    "name": "Milk 2L",
    "brand": "woolworths",
    "price": 2.50,
    "size": "2L",
    "on_special": False,
}


@pytest.fixture(autouse=True)
def reset_limits():
    clear_rate_limits()
    yield
    clear_rate_limits()


@pytest.fixture
def client():
    return TestClient(app)


def test_health_not_rate_limited(client):
    for _ in range(40):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@patch("services.compare.search_coles")
@patch("services.compare.search_woolworths")
def test_compare_rate_limited_after_limit(
    mock_woolworths, mock_coles, client, monkeypatch
):
    mock_woolworths.return_value = [MOCK_MILK]
    mock_coles.return_value = [{**MOCK_MILK, "brand": "coles", "price": 3.20}]
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "3")

    for _ in range(3):
        response = client.post("/api/compare", json={"items": ["milk"]})
        assert response.status_code == 200

    response = client.post("/api/compare", json={"items": ["milk"]})
    assert response.status_code == 429
    assert response.json() == {
        "detail": "Rate limit exceeded. Try again shortly.",
    }


@patch("routers.receipt.extract_items_from_receipt")
def test_receipt_rate_limited_after_limit(mock_extract, client, monkeypatch):
    mock_extract.return_value = ["milk"]
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")

    for _ in range(2):
        response = client.post(
            "/api/receipt",
            json={"image": "abc", "mime_type": "image/jpeg"},
        )
        assert response.status_code == 200

    response = client.post(
        "/api/receipt",
        json={"image": "abc", "mime_type": "image/jpeg"},
    )
    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded. Try again shortly."
