"""Lightweight Terraform (.tf) HCL parser.

Extracts resource blocks, their attributes, and nested sub-blocks
without requiring an external HCL library.
"""

from __future__ import annotations

import re
from typing import Any

from app.scanner.models import ParsedResource

# Matches: resource "aws_s3_bucket" "my_bucket" {
_RESOURCE_RE = re.compile(r'^resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', re.MULTILINE)

# Matches simple key = "value" or key = value
_ATTR_RE = re.compile(r"^\s*([a-z_][a-z0-9_]*)\s*=\s*(.+)", re.IGNORECASE)

# Matches nested block header:  ingress {  or  versioning {
_BLOCK_RE = re.compile(r"^\s*([a-z_][a-z0-9_]*)\s*\{", re.IGNORECASE)


class TerraformParser:
    """Parse raw Terraform content into structured resources."""

    def parse(self, content: str) -> list[ParsedResource]:
        resources: list[ParsedResource] = []

        for match in _RESOURCE_RE.finditer(content):
            res_type = match.group(1)
            res_name = match.group(2)
            block_start_offset = match.end()

            # Find the line number of the resource declaration
            line_start = content[: match.start()].count("\n") + 1

            # Extract the block body between the opening { and its matching }
            raw_block, line_end = self._extract_block(
                content, block_start_offset, line_start
            )

            attributes, blocks = self._parse_block_body(raw_block)

            resources.append(
                ParsedResource(
                    resource_type=res_type,
                    name=res_name,
                    attributes=attributes,
                    blocks=blocks,
                    line_start=line_start,
                    line_end=line_end,
                    raw_block=content[
                        match.start() : match.start()
                        + len(match.group(0))
                        + len(raw_block)
                        + 1
                    ],
                )
            )

        return resources

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_block(
        self, content: str, start: int, line_start: int
    ) -> tuple[str, int]:
        """Return the text inside a brace-delimited block and its ending line."""
        depth = 1
        pos = start
        while pos < len(content) and depth > 0:
            ch = content[pos]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            pos += 1

        body = content[start : pos - 1]
        line_end = line_start + body.count("\n")
        return body, line_end

    def _parse_block_body(
        self, body: str
    ) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
        """Parse a block body into flat attributes and nested sub-blocks."""
        attributes: dict[str, Any] = {}
        blocks: dict[str, list[dict[str, Any]]] = {}
        lines = body.splitlines()
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith("#") or line.startswith("//"):
                i += 1
                continue

            # Check for heredoc: key = <<EOF or key = <<-EOF
            heredoc_match = re.match(
                r"^\s*([a-z_][a-z0-9_]*)\s*=\s*<<-?\s*(\w+)", line, re.IGNORECASE
            )
            if heredoc_match:
                key = heredoc_match.group(1)
                delimiter = heredoc_match.group(2)
                heredoc_lines: list[str] = []
                i += 1
                while i < len(lines):
                    if lines[i].strip() == delimiter:
                        break
                    heredoc_lines.append(lines[i])
                    i += 1
                attributes[key] = "\n".join(heredoc_lines)
                i += 1
                continue

            # Check for nested block:  name {
            block_match = _BLOCK_RE.match(line)
            if block_match and "=" not in line.split("{")[0]:
                block_name = block_match.group(1)
                # Collect until matching }
                sub_body_lines: list[str] = []
                depth = 1
                i += 1
                while i < len(lines) and depth > 0:
                    sub_line = lines[i]
                    if "{" in sub_line:
                        depth += sub_line.count("{")
                    if "}" in sub_line:
                        depth -= sub_line.count("}")
                    if depth > 0:
                        sub_body_lines.append(sub_line)
                    i += 1
                sub_attrs = self._parse_flat_attrs("\n".join(sub_body_lines))
                blocks.setdefault(block_name, []).append(sub_attrs)
                continue

            # Check for attribute
            attr_match = _ATTR_RE.match(line)
            if attr_match:
                key = attr_match.group(1)
                raw_value = attr_match.group(2).strip().rstrip(",")
                attributes[key] = self._coerce_value(raw_value)

            i += 1

        return attributes, blocks

    def _parse_flat_attrs(self, body: str) -> dict[str, Any]:
        """Parse only flat key = value pairs from a block body."""
        attrs: dict[str, Any] = {}
        for line in body.splitlines():
            m = _ATTR_RE.match(line.strip())
            if m:
                attrs[m.group(1)] = self._coerce_value(m.group(2).strip().rstrip(","))
        return attrs

    def _coerce_value(self, raw: str) -> Any:
        """Coerce a raw HCL value string to a Python type."""
        # Booleans
        if raw == "true":
            return True
        if raw == "false":
            return False

        # Numbers
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except ValueError:
            pass

        # Quoted strings — strip outer quotes
        if (raw.startswith('"') and raw.endswith('"')) or (
            raw.startswith("'") and raw.endswith("'")
        ):
            return raw[1:-1]

        # Lists like ["0.0.0.0/0"]
        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            if not inner:
                return []
            items = [
                self._coerce_value(item.strip()) for item in self._split_list(inner)
            ]
            return items

        return raw

    def _split_list(self, inner: str) -> list[str]:
        """Split a comma-separated list, respecting quoted strings."""
        items: list[str] = []
        current: list[str] = []
        in_quote = False
        for ch in inner:
            if ch == '"' and not in_quote:
                in_quote = True
                current.append(ch)
            elif ch == '"' and in_quote:
                in_quote = False
                current.append(ch)
            elif ch == "," and not in_quote:
                items.append("".join(current).strip())
                current = []
            else:
                current.append(ch)
        if current:
            items.append("".join(current).strip())
        return items
