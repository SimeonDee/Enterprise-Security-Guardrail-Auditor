from app.models.guardrail import Severity
from app.services.scanner import ScannerService, SEVERITY_WEIGHTS


def test_severity_weights_exist():
    assert SEVERITY_WEIGHTS["critical"] == 10.0
    assert SEVERITY_WEIGHTS["high"] == 7.0
    assert SEVERITY_WEIGHTS["medium"] == 4.0
    assert SEVERITY_WEIGHTS["low"] == 1.0


def test_extract_resource_name():
    lines = [
        'resource "aws_s3_bucket" "my_bucket" {',
        '  bucket = "test"',
        '  acl    = "public-read"',
        "}",
    ]
    service = ScannerService.__new__(ScannerService)
    name = service._extract_resource_name(lines, 3)
    assert name == "aws_s3_bucket.my_bucket"


def test_extract_resource_name_fallback():
    lines = ["some_config = true"]
    service = ScannerService.__new__(ScannerService)
    name = service._extract_resource_name(lines, 1)
    assert name == "line-1"
