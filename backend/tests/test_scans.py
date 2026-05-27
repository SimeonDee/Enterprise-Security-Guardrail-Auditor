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
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert data["page"] == 1
    assert "total_pages" in data


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


# ---- Pagination tests ----


@pytest.mark.asyncio
async def test_list_scans_pagination(client):
    """Create 3 scans and paginate with page_size=2."""
    for i in range(3):
        await client.post(
            "/api/v1/scans/",
            json={
                "name": f"Page Test {i}",
                "file_type": "terraform",
                "source_content": TERRAFORM_CLEAN,
                "file_name": "clean.tf",
            },
        )
    # Page 1
    resp = await client.get("/api/v1/scans/?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["total_pages"] == 2

    # Page 2
    resp2 = await client.get("/api/v1/scans/?page=2&page_size=2")
    data2 = resp2.json()
    assert len(data2["items"]) == 1
    assert data2["page"] == 2


@pytest.mark.asyncio
async def test_list_scans_filter_by_status(client):
    await client.post(
        "/api/v1/scans/",
        json={
            "name": "Status Filter",
            "file_type": "terraform",
            "source_content": TERRAFORM_CLEAN,
            "file_name": "clean.tf",
        },
    )
    resp = await client.get("/api/v1/scans/?status=completed")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["status"] == "completed"


@pytest.mark.asyncio
async def test_list_scans_filter_by_file_type(client):
    await client.post(
        "/api/v1/scans/",
        json={
            "name": "Type Filter",
            "file_type": "terraform",
            "source_content": TERRAFORM_CLEAN,
            "file_name": "clean.tf",
        },
    )
    resp = await client.get("/api/v1/scans/?file_type=terraform")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    resp2 = await client.get("/api/v1/scans/?file_type=cloudformation")
    assert resp2.json()["total"] == 0


# ---- File upload tests ----


@pytest.mark.asyncio
async def test_upload_tf_file(client):
    content = TERRAFORM_PUBLIC_S3.encode("utf-8")
    response = await client.post(
        "/api/v1/scans/upload?name=Upload+Test",
        files={"file": ("main.tf", content, "text/plain")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["file_name"] == "main.tf"
    assert data["status"] == "completed"
    assert data["total_violations"] >= 1


@pytest.mark.asyncio
async def test_upload_non_tf_file_rejected(client):
    response = await client.post(
        "/api/v1/scans/upload?name=Bad+Upload",
        files={"file": ("config.yaml", b"key: value", "text/plain")},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upload_empty_file_rejected(client):
    response = await client.post(
        "/api/v1/scans/upload?name=Empty+Upload",
        files={"file": ("empty.tf", b"", "text/plain")},
    )
    assert response.status_code == 422
