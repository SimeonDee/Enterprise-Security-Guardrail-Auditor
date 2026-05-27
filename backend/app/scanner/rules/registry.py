"""Auto-discovery registry for security rules."""

from __future__ import annotations

from app.scanner.rules.base import BaseRule


class RuleRegistry:
    """Collects and serves rule instances."""

    def __init__(self) -> None:
        self._rules: list[BaseRule] = []

    def register(self, rule: BaseRule) -> None:
        self._rules.append(rule)

    @property
    def rules(self) -> list[BaseRule]:
        return list(self._rules)

    def get_rules_for(self, resource_type: str) -> list[BaseRule]:
        """Return only rules that apply to the given resource type."""
        return [r for r in self._rules if resource_type in r.resource_types]


def build_default_registry() -> RuleRegistry:
    """Create a registry pre-loaded with all built-in rules."""
    from app.scanner.rules.encryption import DisabledEncryptionRule
    from app.scanner.rules.iam_wildcard import WildcardIAMRule
    from app.scanner.rules.open_ssh import OpenSSHRule
    from app.scanner.rules.public_db import PublicDatabaseRule
    from app.scanner.rules.s3_public import PublicS3Rule

    registry = RuleRegistry()
    registry.register(PublicS3Rule())
    registry.register(OpenSSHRule())
    registry.register(PublicDatabaseRule())
    registry.register(DisabledEncryptionRule())
    registry.register(WildcardIAMRule())
    return registry
