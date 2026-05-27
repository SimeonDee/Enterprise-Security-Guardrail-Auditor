import pytest


@pytest.mark.asyncio
async def test_response_has_request_id(client):
    response = await client.get("/api/v1/health/")
    assert response.status_code == 200
    assert "x-request-id" in response.headers


@pytest.mark.asyncio
async def test_not_found_returns_structured_error(client):
    response = await client.get("/api/v1/guardrails/99999")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"] == "NOT_FOUND"
    assert "detail" in data
