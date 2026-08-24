#!/usr/bin/env python3
"""
UNIT TESTS FOR APEX MONOLITH DEV FORK MANAGER
"""

import sys
from pathlib import Path

# Add scripts directory
sys.path.insert(0, "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts")
from apex_fork_manager import ApexForkManager, ForkRegistryEntry


def test_fork_discovery():
    forks = ApexForkManager.discover_forks()
    assert len(forks) >= 4
    names = [f.name for f in forks]
    assert "antigravity-cli" in names or "apex-core" in names or "CYBERTACK-1FDV-23-0001009" in names


def test_repo_audit_compliance():
    repo = Path("/Users/kcbflux/antigravity-cli")
    entry = ApexForkManager.audit_repo(repo)
    assert isinstance(entry, ForkRegistryEntry)
    assert entry.name == "antigravity-cli"
    assert entry.has_weekly_workflow is True
    assert entry.has_sync_script is True
    assert entry.status == "🟢 COMPLIANT"


def test_overlay_initialization(tmp_path):
    import subprocess
    repo = tmp_path / "mock_fork_repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, capture_output=True)

    ok = ApexForkManager.initialize_overlay(repo, upstream_url="https://github.com/example/upstream.git")
    assert ok is True
    assert (repo / ".github" / "workflows" / "weekly-upstream-sync.yml").exists()
    assert (repo / "scripts" / "sync_upstream.py").exists()
    assert (repo / "extensions").exists()
    assert (repo / "plugins").exists()

    entry = ApexForkManager.audit_repo(repo)
    assert entry.status == "🟢 COMPLIANT"
