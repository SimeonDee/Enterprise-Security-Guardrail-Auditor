import pytest

GUARDRAIL_PAYLOAD = {
    "name": "Dashboard Test Rule",
    "description": "Test rule for dashboard",
    "severity": "high",
    "provider": "aws",
    "resource_type": "aws_s3_bucket",
    "pattern": r"acl\s*=\s*\"public-read\"",
    "remediation": "Fix it.",
}

TERRAFORM_CONTENT = """
resource "aws_s3_bucket" "data" {
  bucket = "test"
  acl    = "public-read"
}
"""


@pytest.mark.asyncio
async def test_dashboard_summary_empty(client):
    response = await client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_scans"] == 0
    assert data["total_violations"] == 0
    assert data["average_risk_score"] == 0.0


@pytest.mark.asyncio
async def test_dashboard_summary_with_data(client):
    await client.post("/api/v1/guardrails/", json=GUARDRAIL_PAYLOAD)
    scan_payload = {
        "name": "Dashboard Scan",
        "file_type": "terraform",
        "source_content": TERRAFORM_CONTENT,
        "file_name": "main.tf",
    }
    await client.post("/api/v1/scans/", json=scan_payload)

    response = await client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_scans"] == 1
    assert data["total_violations"] >= 1
    assert len(data["recent_scans"]) == 1
