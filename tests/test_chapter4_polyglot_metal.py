#!/usr/bin/env python3
"""
Test Suite: Chapter IV - Tower of Babel 51-Floor Polyglot Systems & Hardware Accelerator
Standard: L2 Epistemic Unit Assertion & Invariant Verification
"""

import json
import sys
import unittest
from pathlib import Path

INFRA = Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core")
sys.path.insert(0, str(INFRA / "metal"))
sys.path.insert(0, str(INFRA / "sentinel"))
sys.path.insert(0, str(INFRA / "polyglot"))

from apex_metal_engine import ApexVectorComputeEngine
from apex_sentinel_daemon import ApexSentinelMonitor
from polyglot_engine import TowerOfBabelEngine


class TestChapter4PolyglotAndMetal(unittest.TestCase):
    def test_metal_kernel_source_exists(self):
        metal_file = INFRA / "metal" / "vector_cosine_kernel.metal"
        self.assertTrue(metal_file.exists())
        content = metal_file.read_text()
        self.assertIn("cosine_similarity_kernel", content)
        self.assertIn("metal_stdlib", content)

    def test_metal_vector_compute_engine_benchmark(self):
        engine = ApexVectorComputeEngine(vector_dim=64)
        res = engine.benchmark(num_vectors=1000)
        self.assertEqual(res["vectors_evaluated"], 1000)
        self.assertGreater(res["throughput_vectors_per_second"], 0)
        self.assertGreater(res["top_similarity_score"], 0.0)

    def test_ebpf_sentinel_monitor_and_violation_guard(self):
        monitor = ApexSentinelMonitor()
        # Normal read
        evt1 = monitor.record_access(1234, "kilo", "sys_enter_openat", "/Users/kcbflux/APEX_SYSTEM/AGENTS.md", "r")
        self.assertFalse(evt1.is_violation)

        # Destructive write to protected env
        evt2 = monitor.record_access(1234, "rogue_proc", "sys_enter_write", "/Users/kcbflux/.env", "w")
        self.assertTrue(evt2.is_violation)
        self.assertEqual(len(monitor.violations), 1)

        audit = monitor.audit_active_processes()
        self.assertEqual(audit["status"], "SECURE")
        self.assertEqual(audit["violations_detected"], 1)

    def test_tower_of_babel_polyglot_status_and_verification(self):
        engine = TowerOfBabelEngine()
        status = engine.get_status()
        self.assertEqual(status["total_supported_floors"], 51)
        self.assertGreaterEqual(status["locally_active_compilers"], 3)

        # Verify Python snippet compilation
        res = engine.verify_snippet("Python", "def add(a: int, b: int) -> int: return a + b")
        self.assertEqual(res["status"], "PASSED")
        self.assertEqual(res["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
