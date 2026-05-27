import pytest

TERRAFORM_PUBLIC_S3 = """
resource "aws_s3_bucket" "data" {
  bucket = "my-public-bucket"
  acl    = "public-read"
}
"""

TERRAFORM_OPEN_SSH = """
resource "aws_security_group" "allow_ssh" {
  name = "allow_ssh"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
"""

TERRAFORM_CLEAN = """
resource "aws_s3_bucket" "private" {
  bucket = "my-private-bucket"
  acl    = "private"
}
"""

GUARDRAIL_PUBLIC_S3 = {
    "name": "Public S3 Bucket ACL",
    "description": "S3 bucket has a public ACL",
    "severity": "critical",
    "provider": "aws",
    "resource_type": "aws_s3_bucket",
    "pattern": r"acl\s*=\s*\"(public-read|public-read-write)\"",
    "remediation": "Set the ACL to private.",
}

GUARDRAIL_OPEN_SSH = {
    "name": "Open SSH Port",
    "description": "Security group allows SSH from any IP",
    "severity": "critical",
    "provider": "aws",
    "resource_type": "aws_security_group",
    "pattern": r"from_port\s*=\s*22",
    "remediation": "Restrict SSH to specific CIDRs.",
}


@pytest.mark.asyncio
async def test_scan_finds_public_s3(client):
    await client.post("/api/v1/guardrails/", json=GUARDRAIL_PUBLIC_S3)
    scan_payload = {
        "name": "Test S3 Scan",
        "file_type": "terraform",
        "source_content": TERRAFORM_PUBLIC_S3,
        "file_name": "main.tf",
    }
    response = await client.post("/api/v1/scans/", json=scan_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "completed"
    assert data["total_violations"] >= 1
    assert data["risk_score"] > 0


@pytest.mark.asyncio
async def test_scan_finds_open_ssh(client):
    await client.post("/api/v1/guardrails/", json=GUARDRAIL_OPEN_SSH)
    scan_payload = {
        "name": "Test SSH Scan",
        "file_type": "terraform",
        "source_content": TERRAFORM_OPEN_SSH,
        "file_name": "security.tf",
    }
    response = await client.post("/api/v1/scans/", json=scan_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["total_violations"] >= 1


@pytest.mark.asyncio
async def test_scan_clean_file(client):
    await client.post("/api/v1/guardrails/", json=GUARDRAIL_PUBLIC_S3)
    scan_payload = {
        "name": "Clean Scan",
        "file_type": "terraform",
        "source_content": TERRAFORM_CLEAN,
        "file_name": "clean.tf",
    }
    response = await client.post("/api/v1/scans/", json=scan_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["total_violations"] == 0
    assert data["risk_score"] == 0.0


@pytest.mark.asyncio
async def test_list_scans(client):
    await client.post("/api/v1/guardrails/", json=GUARDRAIL_PUBLIC_S3)
    scan_payload = {
        "name": "List Test",
        "file_type": "terraform",
        "source_content": TERRAFORM_PUBLIC_S3,
        "file_name": "main.tf",
    }
    await client.post("/api/v1/scans/", json=scan_payload)
    response = await client.get("/api/v1/scans/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_scan_detail(client):
    await client.post("/api/v1/guardrails/", json=GUARDRAIL_PUBLIC_S3)
    scan_payload = {
        "name": "Detail Test",
        "file_type": "terraform",
        "source_content": TERRAFORM_PUBLIC_S3,
        "file_name": "main.tf",
    }
    create_resp = await client.post("/api/v1/scans/", json=scan_payload)
    scan_id = create_resp.json()["id"]
    response = await client.get(f"/api/v1/scans/{scan_id}")
    assert response.status_code == 200
    data = response.json()
    assert "violations" in data
    assert "source_content" in data


@pytest.mark.asyncio
async def test_get_scan_not_found(client):
    response = await client.get("/api/v1/scans/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_scan(client):
    await client.post("/api/v1/guardrails/", json=GUARDRAIL_PUBLIC_S3)
    scan_payload = {
        "name": "Delete Test",
        "file_type": "terraform",
        "source_content": TERRAFORM_PUBLIC_S3,
        "file_name": "main.tf",
    }
    create_resp = await client.post("/api/v1/scans/", json=scan_payload)
    scan_id = create_resp.json()["id"]
    response = await client.delete(f"/api/v1/scans/{scan_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_scan_not_found(client):
    response = await client.delete("/api/v1/scans/999")
    assert response.status_code == 404
