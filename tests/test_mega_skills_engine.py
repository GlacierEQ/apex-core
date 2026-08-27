"""
APEX UNIT TEST SUITE: MEGA SKILLS AUDITOR & CONSOLIDATION ENGINE
Standard: L2 Empirical Verification of Mega Skills taxonomy, cognitive firewalls,
          and lossless consolidation invariants.
"""

import sys
from pathlib import Path

# Add INFRASTRUCTURE directory to sys.path
INFRA_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(INFRA_DIR))

from merge_skills import APEX_MEGA_TAXONOMY, ApexSkillsEngine, SkillAuditReport


def test_taxonomy_completeness():
    """Verify that all 8 Mega Skills and 83 Sub-Skills are canonically defined."""
    assert len(APEX_MEGA_TAXONOMY) == 8
    total_sub_skills = sum(len(v["skills"]) for v in APEX_MEGA_TAXONOMY.values())
    assert total_sub_skills == 83


def test_firewall_formatting():
    """Verify that cognitive firewall generator creates valid Markdown interceptor gates."""
    engine = ApexSkillsEngine()
    banner = engine.format_firewall("mega-gcp-data-engineering")
    assert "COGNITIVE FIREWALL" in banner
    assert "INTERCEPTOR GATE" in banner
    assert "BigQuery" in banner


def test_all_mega_skills_audit_green():
    """Verify that all 8 Mega Skills pass audit with 100% green status and no dead paths."""
    engine = ApexSkillsEngine()
    reports = engine.audit_all()

    assert len(reports) == 8
    for r in reports:
        assert r.exists is True, f"{r.name} SKILL.md does not exist"
        assert r.status == "PASS", f"{r.name} failed audit: {r.messages}"
        assert r.has_firewall is True, f"{r.name} missing cognitive firewall"
        assert len(r.dead_paths) == 0, f"{r.name} contains dead paths: {r.dead_paths}"
        assert r.declared_count == len(r.actual_sub_skills), (
            f"{r.name} count mismatch: declared {r.declared_count} != actual {len(r.actual_sub_skills)}"
        )


def test_sub_skill_counts_per_mega_skill():
    """Verify exact expected sub-skill distribution."""
    engine = ApexSkillsEngine()
    expected_counts = {
        "mega-agent-core-operations": 7,
        "mega-apex-sovereign-mastermind": 8,
        "mega-filesystem-omni-engine": 7,
        "mega-gcp-data-engineering": 23,
        "mega-legal-forensic-engine": 5,
        "mega-model-expansion-engine": 3,
        "mega-supabase-ecosystem": 5,
        "mega-vercel-ecosystem": 25,
    }

    for name, expected in expected_counts.items():
        report = engine.audit_mega_skill(name)
        assert len(report.actual_sub_skills) == expected, (
            f"{name}: expected {expected} sub-skills, got {len(report.actual_sub_skills)}"
        )
