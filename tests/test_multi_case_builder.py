#!/usr/bin/env python3
"""
UNIT TESTS FOR APEX MULTI-CASE SYNTHESIZER
"""

import sys
from pathlib import Path

# Add legal tech directory
sys.path.insert(0, "/Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE/LEGAL_TECH")
from apex_multi_case_builder import ApexMasterMultiCaseBuilder


def test_build_all_5_cases():
    built = ApexMasterMultiCaseBuilder.build_all_5_cases()
    assert isinstance(built, dict)
    assert len(built) >= 5

    # Verify all 5 case folders exist
    cases_dir = Path("/Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE/LEGAL_DATA/CASES_BUILT")
    expected_folders = [
        "01_STATE_EMERGENCY_VACATUR_1FDV230001009",
        "02_FEDERAL_CIVIL_RIGHTS_1983_CFAA",
        "03_ODC_DISCIPLINARY_PROSECUTION_BROWER",
        "04_FBI_DOJ_CRIMINAL_REFERRAL",
        "05_KEKOA_REUNION_MANDAMUS_HABEAS",
    ]
    for ef in expected_folders:
        fpath = cases_dir / ef
        assert fpath.exists(), f"Missing case folder: {ef}"
        assert len(list(fpath.glob("*.md"))) > 0
