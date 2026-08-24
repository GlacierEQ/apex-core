#!/usr/bin/env python3
"""
UNIT TESTS FOR APEX COURT PLEADING SYNTHESIZER
"""

import sys
from pathlib import Path

# Add domains directory
sys.path.insert(0, "/Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE")
from apex_pleading_builder import ApexPleadingBuilder


def test_timeline_loading():
    timeline = ApexPleadingBuilder.load_timeline()
    assert "docket" in timeline
    assert timeline["total_items"] > 0
    assert len(timeline["items"]) > 0


def test_rule_60b4_motion_generation():
    timeline = ApexPleadingBuilder.load_timeline()
    motion_md = ApexPleadingBuilder.generate_rule_60b4_motion(timeline)
    assert "Rule 60(b)(4)" in motion_md
    assert "39 seconds" in motion_md or "39-Second" in motion_md
    assert "CASEY BARTON" in motion_md
    assert "SCOT STUART BROWER" in motion_md.upper()
    assert "SHA-256" in motion_md


def test_federal_complaint_generation():
    timeline = ApexPleadingBuilder.load_timeline()
    complaint_md = ApexPleadingBuilder.generate_federal_complaint(timeline)
    assert "42 U.S.C. § 1983" in complaint_md
    assert "Computer Fraud and Abuse Act" in complaint_md
    assert "LeaseWeb" in complaint_md


def test_affidavit_generation():
    timeline = ApexPleadingBuilder.load_timeline()
    affidavit_md = ApexPleadingBuilder.generate_affidavit_of_provenance(timeline)
    assert "FRE 902(13)" in affidavit_md or "902(13)" in affidavit_md
    assert "AFFIDAVIT OF FORENSIC PROVENANCE" in affidavit_md


def test_synthesize_all_to_directory(tmp_path):
    res = ApexPleadingBuilder.synthesize_all(output_dir=tmp_path)
    assert res["rule60b4"].exists()
    assert res["federal_complaint"].exists()
    assert res["affidavit"].exists()
