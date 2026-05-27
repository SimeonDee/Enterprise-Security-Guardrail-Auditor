import pytest

GUARDRAIL_PAYLOAD = {
    "name": "Test Public S3",
    "description": "S3 bucket with public ACL",
    "severity": "critical",
    "provider": "aws",
    "resource_type": "aws_s3_bucket",
    "pattern": r"acl\s*=\s*\"public-read\"",
    "remediation": "Set ACL to private",
}


@pytest.mark.asyncio
async def test_create_guardrail(client):
    response = await client.post("/api/v1/guardrails/", json=GUARDRAIL_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == GUARDRAIL_PAYLOAD["name"]
    assert data["severity"] == "critical"


@pytest.mark.asyncio
async def test_create_duplicate_guardrail(client):
    await client.post("/api/v1/guardrails/", json=GUARDRAIL_PAYLOAD)
    response = await client.post("/api/v1/guardrails/", json=GUARDRAIL_PAYLOAD)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_guardrails(client):
    await client.post("/api/v1/guardrails/", json=GUARDRAIL_PAYLOAD)
    response = await client.get("/api/v1/guardrails/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_guardrail(client):
    create_resp = await client.post("/api/v1/guardrails/", json=GUARDRAIL_PAYLOAD)
    gid = create_resp.json()["id"]
    response = await client.get(f"/api/v1/guardrails/{gid}")
    assert response.status_code == 200
    assert response.json()["id"] == gid


@pytest.mark.asyncio
async def test_get_guardrail_not_found(client):
    response = await client.get("/api/v1/guardrails/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_guardrail(client):
    create_resp = await client.post("/api/v1/guardrails/", json=GUARDRAIL_PAYLOAD)
    gid = create_resp.json()["id"]
    response = await client.patch(f"/api/v1/guardrails/{gid}", json={"enabled": False})
    assert response.status_code == 200
    assert response.json()["enabled"] is False


@pytest.mark.asyncio
async def test_update_guardrail_not_found(client):
    response = await client.patch("/api/v1/guardrails/999", json={"enabled": False})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_guardrail(client):
    create_resp = await client.post("/api/v1/guardrails/", json=GUARDRAIL_PAYLOAD)
    gid = create_resp.json()["id"]
    response = await client.delete(f"/api/v1/guardrails/{gid}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_guardrail_not_found(client):
    response = await client.delete("/api/v1/guardrails/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_filter_guardrails_by_enabled(client):
    await client.post("/api/v1/guardrails/", json=GUARDRAIL_PAYLOAD)
    response = await client.get("/api/v1/guardrails/?enabled=true")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get("/api/v1/guardrails/?enabled=false")
    assert response.status_code == 200
    assert len(response.json()) == 0
