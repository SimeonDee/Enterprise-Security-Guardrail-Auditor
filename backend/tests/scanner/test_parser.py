"""Tests for the Terraform parser."""

from app.scanner.parser import TerraformParser

parser = TerraformParser()


SIMPLE_RESOURCE = """
resource "aws_s3_bucket" "data" {
  bucket = "my-bucket"
  acl    = "private"
}
"""

MULTI_RESOURCE = """
resource "aws_s3_bucket" "data" {
  bucket = "my-bucket"
  acl    = "public-read"
}

resource "aws_security_group" "web" {
  name = "web-sg"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
"""

NESTED_BLOCKS = """
resource "aws_security_group" "allow_ssh" {
  name = "allow_ssh"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
"""

BOOLEAN_AND_NUMBER_ATTRS = """
resource "aws_db_instance" "main" {
  engine            = "postgres"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  storage_encrypted = false
  publicly_accessible = true
  port              = 5432
}
"""


def test_parse_simple_resource():
    resources = parser.parse(SIMPLE_RESOURCE)
    assert len(resources) == 1
    r = resources[0]
    assert r.resource_type == "aws_s3_bucket"
    assert r.name == "data"
    assert r.full_name == "aws_s3_bucket.data"
    assert r.attributes["bucket"] == "my-bucket"
    assert r.attributes["acl"] == "private"


def test_parse_multiple_resources():
    resources = parser.parse(MULTI_RESOURCE)
    assert len(resources) == 2
    types = {r.resource_type for r in resources}
    assert types == {"aws_s3_bucket", "aws_security_group"}


def test_parse_nested_blocks():
    resources = parser.parse(NESTED_BLOCKS)
    assert len(resources) == 1
    sg = resources[0]
    assert "ingress" in sg.blocks
    assert "egress" in sg.blocks
    assert len(sg.blocks["ingress"]) == 1
    assert len(sg.blocks["egress"]) == 1
    ingress = sg.blocks["ingress"][0]
    assert ingress["from_port"] == 22
    assert ingress["cidr_blocks"] == ["0.0.0.0/0"]


def test_parse_boolean_and_number_coercion():
    resources = parser.parse(BOOLEAN_AND_NUMBER_ATTRS)
    assert len(resources) == 1
    db = resources[0]
    assert db.attributes["storage_encrypted"] is False
    assert db.attributes["publicly_accessible"] is True
    assert db.attributes["allocated_storage"] == 20
    assert db.attributes["port"] == 5432
    assert db.attributes["engine"] == "postgres"


def test_parse_line_numbers():
    resources = parser.parse(SIMPLE_RESOURCE)
    r = resources[0]
    assert r.line_start >= 1
    assert r.line_end >= r.line_start


def test_parse_empty_content():
    resources = parser.parse("")
    assert resources == []


def test_parse_no_resources():
    resources = parser.parse('# Just a comment\nvariable "name" {}\n')
    assert resources == []


def test_raw_block_captured():
    resources = parser.parse(SIMPLE_RESOURCE)
    r = resources[0]
    assert 'bucket = "my-bucket"' in r.raw_block


def test_parse_list_attribute():
    tf = """
resource "aws_security_group" "test" {
  name = "test"
  ingress {
    cidr_blocks = ["10.0.0.0/8", "172.16.0.0/12"]
  }
}
"""
    resources = parser.parse(tf)
    sg = resources[0]
    ingress = sg.blocks["ingress"][0]
    assert ingress["cidr_blocks"] == ["10.0.0.0/8", "172.16.0.0/12"]
