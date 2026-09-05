#!/usr/bin/env python3
"""
APEX Firewall — Action Validation and Security Guardrails
Inspired by mega-skills firewall pattern.

Validates actions against security policies before execution.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ActionType(Enum):
    """Types of actions that can be performed."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DEPLOY = "deploy"
    DELETE = "delete"
    NETWORK = "network"
    CREDENTIAL = "credential"


@dataclass
class SecurityPolicy:
    """Security policy defining allowed and forbidden actions."""
    name: str
    allowed_actions: Set[ActionType] = field(default_factory=set)
    forbidden_actions: Set[ActionType] = field(default_factory=set)
    approval_required: Set[ActionType] = field(default_factory=set)
    description: str = ""

    def is_allowed(self, action: ActionType) -> bool:
        """Check if an action is allowed."""
        if action in self.forbidden_actions:
            return False
        if action in self.allowed_actions:
            return True
        return False

    def needs_approval(self, action: ActionType) -> bool:
        """Check if an action needs approval."""
        return action in self.approval_required


class FirewallViolation(PermissionError):
    """Raised when an action violates security policy."""
    pass


class Firewall:
    """Action firewall for validating operations against security policies."""

    def __init__(self) -> None:
        self.policies: Dict[str, SecurityPolicy] = {}
        self.audit_log: List[Dict[str, Any]] = []

    def register_policy(self, policy: SecurityPolicy) -> None:
        """Register a security policy."""
        self.policies[policy.name] = policy

    def validate(
        self,
        action: ActionType,
        policy_name: str = "default",
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Validate an action against a policy.

        Returns True if allowed, False if approval required.
        Raises FirewallViolation if forbidden.
        """
        policy = self.policies.get(policy_name)
        if not policy:
            raise ValueError(f"Policy not found: {policy_name}")

        if action in policy.forbidden_actions:
            self._log(action, policy_name, "denied", "forbidden", context)
            raise FirewallViolation(
                f"Action {action.value} is forbidden by policy {policy_name}"
            )

        if action in policy.approval_required:
            self._log(action, policy_name, "approval_required", None, context)
            return False

        if action not in policy.allowed_actions:
            self._log(action, policy_name, "denied", "not in allowed list", context)
            raise FirewallViolation(
                f"Action {action.value} is not allowed by policy {policy_name}"
            )

        self._log(action, policy_name, "allowed", None, context)
        return True

    def _log(
        self,
        action: ActionType,
        policy: str,
        result: str,
        reason: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an action attempt."""
        entry: Dict[str, Any] = {
            "timestamp": time.time(),
            "action": action.value,
            "policy": policy,
            "result": result,
        }
        if reason:
            entry["reason"] = reason
        if context:
            entry["context"] = str(context)[:200]
        self.audit_log.append(entry)

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get the audit log."""
        return self.audit_log.copy()

    def clear_audit_log(self) -> None:
        """Clear the audit log."""
        self.audit_log = []

    def get_stats(self) -> Dict[str, Any]:
        """Get firewall statistics."""
        total = len(self.audit_log)
        allowed = sum(1 for e in self.audit_log if e["result"] == "allowed")
        denied = sum(1 for e in self.audit_log if e["result"] == "denied")
        approval = sum(
            1 for e in self.audit_log if e["result"] == "approval_required"
        )

        return {
            "total_actions": total,
            "allowed": allowed,
            "denied": denied,
            "approval_required": approval,
            "policies_count": len(self.policies),
        }


# ─── Default Policies ────────────────────────────────────────────────────────

DEFAULT_POLICY = SecurityPolicy(
    name="default",
    allowed_actions={ActionType.READ, ActionType.WRITE, ActionType.EXECUTE},
    forbidden_actions={ActionType.DELETE, ActionType.CREDENTIAL},
    approval_required={ActionType.DEPLOY, ActionType.NETWORK},
    description="Default security policy",
)

STRICT_POLICY = SecurityPolicy(
    name="strict",
    allowed_actions={ActionType.READ},
    forbidden_actions={
        ActionType.WRITE,
        ActionType.DELETE,
        ActionType.DEPLOY,
        ActionType.NETWORK,
        ActionType.CREDENTIAL,
    },
    approval_required={ActionType.EXECUTE},
    description="Strict read-only policy",
)

DEPLOY_POLICY = SecurityPolicy(
    name="deploy",
    allowed_actions={ActionType.READ, ActionType.WRITE, ActionType.EXECUTE},
    forbidden_actions={ActionType.CREDENTIAL},
    approval_required={ActionType.DEPLOY, ActionType.DELETE, ActionType.NETWORK},
    description="Deployment policy with approval gates",
)


def create_default_firewall() -> Firewall:
    """Create a firewall with default policies."""
    firewall = Firewall()
    firewall.register_policy(DEFAULT_POLICY)
    firewall.register_policy(STRICT_POLICY)
    firewall.register_policy(DEPLOY_POLICY)
    return firewall
