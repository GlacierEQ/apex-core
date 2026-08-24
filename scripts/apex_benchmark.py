#!/usr/bin/env python3
"""
APEX REAL-TIME MODEL LATENCY & TOKEN BENCHMARKING ENGINE
Standard: Automated measurement of TTFT, throughput (tokens/sec), and latency across all active models.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

GATEWAY_PATH = Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/MCP_SERVERS/openrouter-free-gateway")
if str(GATEWAY_PATH) not in sys.path:
    sys.path.insert(0, str(GATEWAY_PATH))

from server import chat_openrouter, list_free_models


def benchmark_model(model_id: str, test_prompt: str = "Return only the word 'READY' and the number 42.") -> Dict[str, Any]:
    t0 = time.perf_counter()
    res = chat_openrouter(
        model=model_id,
        prompt=test_prompt,
        max_tokens=64,
        temperature=0.0,
    )
    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000.0

    if res.get("status") == "success":
        usage = res.get("usage", {})
        completion_tokens = usage.get("completion_tokens", max(1, len(res.get("response", "").split())))
        tps = (completion_tokens / (t1 - t0)) if (t1 - t0) > 0 else 0.0
        return {
            "model_id": model_id,
            "status": "PASS",
            "latency_ms": round(latency_ms, 2),
            "tokens_per_sec": round(tps, 2),
            "model_used": res.get("model_used", model_id),
            "response_snippet": res.get("response", "").strip()[:40],
        }
    else:
        return {
            "model_id": model_id,
            "status": "FAIL",
            "latency_ms": round(latency_ms, 2),
            "tokens_per_sec": 0.0,
            "error": res.get("message", "Unknown error"),
        }


def run_full_benchmark() -> List[Dict[str, Any]]:
    test_models = [
        "xiaomi/mimo-v2.5-pro",
        "google/gemini-2.0-flash-exp:free",
        "deepseek/deepseek-r1:free",
        "deepseek/deepseek-chat:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "qwen/qwen-2.5-coder-32b-instruct:free",
    ]

    print("=" * 80)
    print("🚀 APEX MULTI-MODEL LIVE LATENCY & THROUGHPUT BENCHMARK")
    print("=" * 80)
    results = []

    for m in test_models:
        print(f"[*] Benchmarking {m:<45} ...", end=" ", flush=True)
        bench = benchmark_model(m)
        if bench["status"] == "PASS":
            print(f"🟢 {bench['latency_ms']:>7.1f}ms | {bench['tokens_per_sec']:>5.1f} tok/s ({bench['model_used']})")
        else:
            print(f"🔴 FAIL ({bench.get('error')[:40]}...)")
        results.append(bench)

    print("=" * 80)
    return results


if __name__ == "__main__":
    run_full_benchmark()
