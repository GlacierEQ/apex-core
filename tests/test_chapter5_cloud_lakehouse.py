#!/usr/bin/env python3
"""
Test Suite: Chapter V - Omniversal Multi-Cloud Fabric & 4TB Lakehouse
Standard: L2 Epistemic Unit Assertion & Invariant Verification
"""

import json
import sys
import unittest
from pathlib import Path

INFRA = Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core")
sys.path.insert(0, str(INFRA / "cloud"))
sys.path.insert(0, str(INFRA / "lakehouse"))
sys.path.insert(0, str(INFRA / "security"))

from cloud_sync_daemon import MultiCloudSyncOrchestrator
from duckdb_vector_lake import ApexVectorLakehouse
from apex_scrubber import scrub_text


class TestChapter5CloudAndLakehouse(unittest.TestCase):
    def test_multi_cloud_sync_orchestrator(self):
        orch = MultiCloudSyncOrchestrator()
        summary = orch.get_summary()
        self.assertEqual(summary["total_horizons"], 4)
        self.assertGreaterEqual(summary["total_storage_lakehouse_tb"], 8.0)
        self.assertTrue(any(h["name"] == "ShadowDrive 4TB Lake" for h in summary["horizons"]))

    def test_vector_lakehouse_storage_and_query(self):
        lake = ApexVectorLakehouse()
        test_entity = [{
            "id": "test-cloud-entity-01",
            "name": "Cloud Mesh Router",
            "path": "cloud/mesh.py",
            "domain": "cloud_network",
            "size": 5120,
            "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        }]
        lake.ingest_entities(test_entity)
        
        hits = lake.query_similarity("cloud mesh router", top_k=2)
        self.assertTrue(len(hits) > 0)
        self.assertTrue(any(h["entity_id"] == "test-cloud-entity-01" for h in hits))
        lake.close()

    def test_air_gapped_secret_and_pii_scrubber(self):
        dirty_input = "Key: sk-ant-api03-12345678901234567890123456789012, Mail: admin@glaciereq.com"
        clean, count = scrub_text(dirty_input)
        self.assertEqual(count, 2)
        self.assertNotIn("sk-ant-", clean)
        self.assertNotIn("admin@glaciereq.com", clean)
        self.assertIn("[REDACTED_ANTHROPIC_KEY]", clean)
        self.assertIn("[REDACTED_EMAIL]", clean)


if __name__ == "__main__":
    unittest.main()
