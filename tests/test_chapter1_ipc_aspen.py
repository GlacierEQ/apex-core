#!/usr/bin/env python3
"""
Test Suite: Chapter I - Aspen Grove Neural IPC Swarm & Mission Control
Standard: L2 Epistemic Unit Assertion & Invariant Verification
"""

import json
import subprocess
import sys
import time
import unittest
from pathlib import Path

INFRA = Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core")
SWARM = Path("/Users/kcbflux/APEX_SYSTEM/DOMAINS/SWARM_INTELLIGENCE/aspen-grove-core")
sys.path.insert(0, str(INFRA / "ipc"))
sys.path.insert(0, str(SWARM))
sys.path.insert(0, str(INFRA / "mission_control"))

from apex_ipc_mesh import ApexIpcRingBuffer, AgentMessagePacket
from aspen_synaptic_engine import AspenSynapticMemory
from apex_mission_control import gather_system_metrics


class TestChapter1NeuralIpcAndAspen(unittest.TestCase):
    def test_capnp_schema_file_exists(self):
        schema_file = INFRA / "ipc" / "advanced_agent_mesh.capnp"
        self.assertTrue(schema_file.exists())
        content = schema_file.read_text()
        self.assertIn("struct AgentMessage", content)
        self.assertIn("struct SynapticWeightUpdate", content)

    def test_ipc_ring_buffer_write_read_roundtrip(self):
        buf = ApexIpcRingBuffer()
        test_pkt = AgentMessagePacket(
            message_id=f"TEST-{int(time.time_ns())}",
            sequence_number=999,
            sender_role="reasoner",
            recipient_role="synthesizer",
            message_type="astBlock",
            epistemic_tier="l2Behavior",
            payload={"assertion": "Zero-copy roundtrip verified", "value": 42},
        )
        seq = buf.write_message(test_pkt)
        self.assertGreater(seq, 0)

        recent = buf.read_latest_messages(5)
        self.assertTrue(len(recent) > 0)
        latest = recent[-1]
        self.assertEqual(latest.sender_role, "reasoner")
        self.assertEqual(latest.recipient_role, "synthesizer")
        self.assertEqual(latest.payload["value"], 42)
        buf.close()

    def test_aspen_hebbian_weight_reinforcement(self):
        mem = AspenSynapticMemory()
        e1, e2 = "test-agent-alpha", "test-agent-beta"
        mem.upsert_entity(e1, "Alpha Agent", "test", "unit")
        mem.upsert_entity(e2, "Beta Agent", "test", "unit")

        reinf = mem.reinforce_cooccurrence([e1, e2])
        self.assertGreaterEqual(reinf, 1)

        recall_res = mem.recall("Alpha Agent", top_k=2)
        self.assertTrue(len(recall_res["primary_matches"]) > 0)
        self.assertTrue(any(h["id"] == e1 for h in recall_res["primary_matches"]))
        mem.close()

    def test_mission_control_metrics_aggregator(self):
        m = gather_system_metrics()
        self.assertEqual(m["status"], "ONLINE")
        self.assertIn("capabilities_total", m)
        self.assertEqual(m["capabilities_total"], 779)
        self.assertIn("ipc", m)
        self.assertIn("synaptic_memory", m)


if __name__ == "__main__":
    unittest.main()
