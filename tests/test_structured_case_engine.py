#!/usr/bin/env python3
"""
UNIT TESTS FOR APEX STRUCTURED CASE ENGINE
"""

import sys
from pathlib import Path

# Add legal tech directory
sys.path.insert(0, "/Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE/LEGAL_TECH")
from apex_structured_case_engine import ApexStructuredCaseEngine, StructuredCase


def test_build_master_case():
    case_obj = ApexStructuredCaseEngine.build_master_cybertack_case()
    assert isinstance(case_obj, StructuredCase)
    assert case_obj.case_id == "1FDV-23-0001009"
    assert "FC-D NO. 1FDV-23-0001009" in case_obj.docket_number
    assert case_obj.claims_count > 0


def test_query_case_dossier():
    dossier = ApexStructuredCaseEngine.query_case_dossier("1FDV-23-0001009")
    assert "case" in dossier
    assert "claims" in dossier
    assert "impeachments" in dossier
    assert len(dossier["claims"]) > 0
    assert len(dossier["impeachments"]) > 0


def test_case_summary_markdown_generation():
    md = ApexStructuredCaseEngine.generate_case_summary_markdown("1FDV-23-0001009")
    assert "STRUCTURED CASE DOSSIER" in md
    assert "CLAIM-001" in md
    assert "Scot Stuart Brower" in md
    assert "39-Second" in md or "39-second" in md.lower()
