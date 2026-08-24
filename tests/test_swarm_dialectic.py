#!/usr/bin/env python3
"""
UNIT TESTS FOR APEX 4-PHASE SWARM DIALECTIC ORCHESTRATOR
"""

import sys
from pathlib import Path

# Add scripts directory
sys.path.insert(0, "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts")
from apex_swarm_dialectic import ApexSwarmDialectic, SwarmDialecticDeliverable


from unittest.mock import patch

def test_swarm_dialectic_structure():
    with patch.object(ApexSwarmDialectic, "dispatch_model") as mock_dispatch:
        mock_dispatch.return_value = ("// Synthesized Spec & Invariant Assertions.", 0.05)
        task = "Design high-throughput Cap'n Proto zero-copy RPC schema"
        deliv = ApexSwarmDialectic.execute_swarm(task, max_refinements=1)

        assert isinstance(deliv, SwarmDialecticDeliverable)
        assert deliv.task == task
        assert deliv.total_phases == 4
        assert deliv.consensus_achieved is True
        assert len(deliv.lead_architect_spec) > 0
        assert len(deliv.synthesized_code) > 0
        assert len(deliv.adversarial_audit_report) > 0
        assert len(deliv.perception_context) > 0
        assert deliv.total_elapsed_seconds >= 0.0


def test_swarm_phase_history_integrity():
    with patch.object(ApexSwarmDialectic, "dispatch_model") as mock_dispatch:
        mock_dispatch.return_value = ("// Synthesized Phase Result.", 0.05)
        task = "Verify SHA-256 Bates stamping invariant for legal evidence lake"
        deliv = ApexSwarmDialectic.execute_swarm(task, max_refinements=1)

        assert len(deliv.history) >= 4
        phases = [h.phase_number for h in deliv.history]
        assert 1 in phases
        assert 2 in phases
        assert 3 in phases
        assert 4 in phases
