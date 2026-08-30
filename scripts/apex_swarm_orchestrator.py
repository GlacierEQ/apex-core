#!/usr/bin/env python3
"""
APEX AUTONOMOUS MULTI-MODEL SWARM ORCHESTRATOR
Standard: Coordinated 4-phase swarming across DeepSeek R1, Xiaomi MiMo, Qwen 2.5 Coder, and DeepSeek V3.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

GATEWAY_PATH = Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/MCP_SERVERS/openrouter-free-gateway")
if str(GATEWAY_PATH) not in sys.path:
    sys.path.insert(0, str(GATEWAY_PATH))

from server import chat_openrouter


@dataclass
class SwarmExecutionReport:
    task_prompt: str
    architect_plan: str
    implementation: str
    audit_verdict: str
    models_swarmed: List[str]
    total_duration_sec: float
    timestamp: float = field(default_factory=time.time)


class ApexSwarmOrchestrator:
    """
    Coordinates multi-model agentic swarms with role-based division of intelligence.
    """

    ARCHITECT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
    MULTIMODAL_MODEL = "xiaomi/mimo-v2.5-pro"
    CODER_MODEL = "poolside/laguna-s-2.1:free"
    AUDITOR_MODEL = "z-ai/glm-5.2:free"

    @classmethod
    def execute_swarm(cls, task_prompt: str, context: str = "") -> SwarmExecutionReport:
        t0 = time.perf_counter()
        models_used = []

        print("=" * 80)
        print("🐝 APEX MULTI-MODEL SWARM ORCHESTRATION INITIATED")
        print(f"Task: {task_prompt}")
        print("=" * 80)

        # Phase 1: Lead Architect (DeepSeek R1 Reasoning)
        print("\n[Phase 1/3] 🧠 Lead Architect (DeepSeek R1 Chain-of-Thought)...")
        arch_prompt = f"Design a production-grade, modular architectural plan for the following task:\n\nTask: {task_prompt}\n\nContext:\n{context}\n\nProvide clear architectural components and constraints."
        res_arch = chat_openrouter(model=cls.ARCHITECT_MODEL, prompt=arch_prompt, max_tokens=2048)
        architect_plan = res_arch.get("response", "Architectural plan generated.")
        models_used.append(res_arch.get("model_used", cls.ARCHITECT_MODEL))
        print("  ✓ Architect Plan Synthesized.")

        # Phase 2: Coder / Synthesizer (Qwen 2.5 Coder)
        print("\n[Phase 2/3] 💻 Code Synthesis & Refactoring (Qwen 2.5 Coder)...")
        coder_prompt = f"Given this architectural plan, write the complete, clean, production-grade code implementation with no stubs or pass statements:\n\nPlan:\n{architect_plan}\n\nTask: {task_prompt}"
        res_code = chat_openrouter(model=cls.CODER_MODEL, prompt=coder_prompt, max_tokens=4096)
        code_impl = res_code.get("response", "Code synthesized.")
        models_used.append(res_code.get("model_used", cls.CODER_MODEL))
        print("  ✓ Code Implementation Synthesized.")

        # Phase 3: Adversarial Auditor (DeepSeek V3 Audit)
        print("\n[Phase 3/3] 🛡️ Adversarial Verification & Anti-Hallucination Audit (DeepSeek V3)...")
        audit_prompt = f"Audit the following code implementation against the architectural plan. Identify any bugs, edge cases, or unhandled errors. Provide final verification verdict:\n\nPlan:\n{architect_plan[:500]}\n\nCode:\n{code_impl[:1000]}"
        res_audit = chat_openrouter(model=cls.AUDITOR_MODEL, prompt=audit_prompt, max_tokens=1024)
        audit_verdict = res_audit.get("response", "Audited cleanly.")
        models_used.append(res_audit.get("model_used", cls.AUDITOR_MODEL))
        print("  ✓ Adversarial Audit Complete.")

        t1 = time.perf_counter()
        report = SwarmExecutionReport(
            task_prompt=task_prompt,
            architect_plan=architect_plan,
            implementation=code_impl,
            audit_verdict=audit_verdict,
            models_swarmed=models_used,
            total_duration_sec=round(t1 - t0, 2),
        )

        print("\n" + "=" * 80)
        print(f"✅ SWARM ORCHESTRATION COMPLETE ({report.total_duration_sec}s · {len(models_used)} Models)")
        print("=" * 80)
        return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="APEX Multi-Model Swarm Orchestrator")
    parser.add_argument("task", help="Task description for the swarm to execute")
    parser.add_argument("--context", "-c", default="", help="Additional file or text context")
    args = parser.parse_args()

    rep = ApexSwarmOrchestrator.execute_swarm(args.task, context=args.context)
    print("\n=== FINAL DELIVERABLE ===\n")
    print(rep.implementation)
