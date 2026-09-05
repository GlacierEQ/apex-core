#!/usr/bin/env python3
"""
Tests for APEX Firewall — Action Validation and Security Guardrails.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from firewall import (
    Firewall,
    SecurityPolicy,
    ActionType,
    FirewallViolation,
    DEFAULT_POLICY,
    STRICT_POLICY,
    DEPLOY_POLICY,
    create_default_firewall,
)


class TestActionType:
    def test_values(self):
        assert ActionType.READ.value == "read"
        assert ActionType.WRITE.value == "write"
        assert ActionType.DELETE.value == "delete"
        assert ActionType.DEPLOY.value == "deploy"

    def test_count(self):
        assert len(list(ActionType)) == 7


class TestSecurityPolicy:
    def test_create(self):
        policy = SecurityPolicy(name="test", description="test")
        assert policy.name == "test"
        assert policy.description == "test"

    def test_is_allowed(self):
        policy = SecurityPolicy(
            name="test",
            allowed_actions={ActionType.READ, ActionType.WRITE},
        )
        assert policy.is_allowed(ActionType.READ) is True
        assert policy.is_allowed(ActionType.WRITE) is True
        assert policy.is_allowed(ActionType.DELETE) is False

    def test_is_allowed_forbidden(self):
        policy = SecurityPolicy(
            name="test",
            allowed_actions={ActionType.READ},
            forbidden_actions={ActionType.DELETE},
        )
        assert policy.is_allowed(ActionType.DELETE) is False

    def test_needs_approval(self):
        policy = SecurityPolicy(
            name="test",
            approval_required={ActionType.DEPLOY},
        )
        assert policy.needs_approval(ActionType.DEPLOY) is True
        assert policy.needs_approval(ActionType.READ) is False


class TestFirewall:
    def test_create_default(self):
        firewall = create_default_firewall()
        assert len(firewall.policies) == 3

    def test_register_policy(self):
        firewall = Firewall()
        policy = SecurityPolicy(name="custom")
        firewall.register_policy(policy)
        assert "custom" in firewall.policies

    def test_validate_allowed(self):
        firewall = create_default_firewall()
        assert firewall.validate(ActionType.READ, "default") is True

    def test_validate_forbidden(self):
        firewall = create_default_firewall()
        with pytest.raises(FirewallViolation):
            firewall.validate(ActionType.DELETE, "default")

    def test_validate_approval_required(self):
        firewall = create_default_firewall()
        result = firewall.validate(ActionType.DEPLOY, "default")
        assert result is False

    def test_validate_policy_not_found(self):
        firewall = Firewall()
        with pytest.raises(ValueError):
            firewall.validate(ActionType.READ, "nonexistent")

    def test_audit_log(self):
        firewall = create_default_firewall()
        firewall.validate(ActionType.READ, "default")
        firewall.validate(ActionType.DEPLOY, "default")
        log = firewall.get_audit_log()
        assert len(log) == 2

    def test_audit_log_with_context(self):
        firewall = create_default_firewall()
        firewall.validate(ActionType.READ, "default", context={"key": "value"})
        log = firewall.get_audit_log()
        assert len(log) == 1
        assert "context" in log[0]

    def test_clear_audit_log(self):
        firewall = create_default_firewall()
        firewall.validate(ActionType.READ, "default")
        firewall.clear_audit_log()
        assert len(firewall.get_audit_log()) == 0

    def test_get_stats(self):
        firewall = create_default_firewall()
        firewall.validate(ActionType.READ, "default")
        stats = firewall.get_stats()
        assert stats["total_actions"] == 1
        assert stats["allowed"] == 1
        assert stats["policies_count"] == 3

    def test_strict_policy(self):
        firewall = Firewall()
        firewall.register_policy(STRICT_POLICY)
        with pytest.raises(FirewallViolation):
            firewall.validate(ActionType.WRITE, "strict")

    def test_deploy_policy(self):
        firewall = Firewall()
        firewall.register_policy(DEPLOY_POLICY)
        assert firewall.validate(ActionType.READ, "deploy") is True
        assert firewall.validate(ActionType.DEPLOY, "deploy") is False


class TestDefaultPolicies:
    def test_default_policy(self):
        assert DEFAULT_POLICY.name == "default"
        assert ActionType.READ in DEFAULT_POLICY.allowed_actions
        assert ActionType.DELETE in DEFAULT_POLICY.forbidden_actions

    def test_strict_policy(self):
        assert STRICT_POLICY.name == "strict"
        assert ActionType.READ in STRICT_POLICY.allowed_actions
        assert ActionType.WRITE in STRICT_POLICY.forbidden_actions

    def test_deploy_policy(self):
        assert DEPLOY_POLICY.name == "deploy"
        assert ActionType.DEPLOY in DEPLOY_POLICY.approval_required


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
