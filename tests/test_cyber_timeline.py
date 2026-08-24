#!/usr/bin/env python3
"""
UNIT TESTS FOR CYBER FORENSICS TIMELINE & ANOMALY DETECTION ENGINE
"""

import sys
from pathlib import Path

# Add scripts and domain directories
sys.path.insert(0, "/Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE")
from cyber_timeline_engine import CyberTimelineEngine, EvidenceItem


def test_sha256_computation(tmp_path):
    f = tmp_path / "exhibit_test.txt"
    f.write_text("CONFIDENTIAL EVIDENCE EXHIBIT 1009", encoding="utf-8")
    h = CyberTimelineEngine.compute_sha256(f)
    assert len(h) == 64
    assert isinstance(h, str)


def test_date_extraction_patterns():
    d1 = CyberTimelineEngine.extract_text_date("MOTION_2024-07-15_FILED.pdf")
    assert d1 == "2024-07-15"

    d2 = CyberTimelineEngine.extract_text_date("EXHIBIT_2023_08_22_AFFIDAVIT.md")
    assert d2 == "2023-08-22"

    d3 = CyberTimelineEngine.extract_text_date("random_doc.txt", "Filed in court on Aug 24, 2024 by counsel")
    assert d3 is not None or "2024" in str(d3)


def test_anomaly_detection_rules():
    # 1. Zero byte anomaly
    item_zero = EvidenceItem(
        item_id="EV-0001",
        file_name="wiped_log.txt",
        relative_path="wiped_log.txt",
        absolute_path="/path/wiped_log.txt",
        file_size_bytes=0,
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        mtime_iso="2024-07-15T12:00:00",
        ctime_iso="2024-07-15T12:00:00",
        extracted_date_iso="2024-07-15",
        vault_source="TEST_VAULT",
    )
    anomalies = CyberTimelineEngine.detect_anomalies(item_zero, "deleted database logs")
    assert any("Zero-byte" in a for a in anomalies)
    assert any("DELETED" in a for a in anomalies)


def test_timeline_report_generation(tmp_path):
    report_file = tmp_path / "TEST_MASTER_TIMELINE.md"
    res = CyberTimelineEngine.generate_timeline_report(output_file=report_file)
    assert res["docket"] == "CYBERTACK-1FDV-23-0001009"
    assert res["total_items"] > 0
    assert report_file.exists()
