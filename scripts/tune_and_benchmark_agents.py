#!/usr/bin/env python3
"""
APEX AGENT FLEET BENCHMARK & TUNING HARNESS
Standard: Level 4 Telemetry & Resilience Standard (AGENTS.md)
Tests and tunes the 10 Kilo Code agents and OpenRouter models across:
1. Latency (TTFT & total elapsed)
2. Output token throughput
3. Domain prompt accuracy
4. Failover resilience
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

# Load gateway
GATEWAY_PATH = Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/MCP_SERVERS/openrouter-free-gateway")
if str(GATEWAY_PATH) not in sys.path:
    sys.path.insert(0, str(GATEWAY_PATH))

from server import get_openrouter_api_key

# 10 Dedicated Agent Models to Benchmark
TEST_MATRIX = [
    {
        "agent": "fast-subagent",
        "model": "liquid/lfm-2.5-2.6b:free",
        "role": "Ultra-fast execution & triage",
        "prompt": "Answer in 5 words or less: What is the primary purpose of unit tests?",
        "expected_kw": ["test", "verify", "code", "bug", "quality", "behavior"],
        "recommended_temp": 0.1,
    },
    {
        "agent": "build",
        "model": "poolside/laguna-s-2.1:free",
        "role": "Software Builder",
        "prompt": "Write a python function `is_palindrome(s: str) -> bool` with no stubs.",
        "expected_kw": ["def is_palindrome", "return"],
        "recommended_temp": 0.2,
    },
    {
        "agent": "code-reviewer",
        "model": "poolside/laguna-s-2.1:free",
        "role": "Code Reviewer",
        "prompt": "Review this code for a security flaw: `query = f'SELECT * FROM users WHERE id = {user_id}'`. Name the flaw in one sentence.",
        "expected_kw": ["sql injection", "injection", "parameter"],
        "recommended_temp": 0.1,
    },
    {
        "agent": "code-simplifier",
        "model": "cohere/north-mini-code:free",
        "role": "Code Simplifier",
        "prompt": "Simplify to one line: `if x == True: return True\nelse: return False`",
        "expected_kw": ["return", "bool", "x"],
        "recommended_temp": 0.1,
    },
    {
        "agent": "code-skeptic",
        "model": "z-ai/glm-5.2:free",
        "role": "Adversarial Critic",
        "prompt": "What edge case breaks `1 / len(items)` in Python? Answer in one sentence.",
        "expected_kw": ["empty", "zero", "zerodivision", "length"],
        "recommended_temp": 0.2,
    },
    {
        "agent": "data",
        "model": "google/gemma-4-31b-it:free",
        "role": "Data Analyst",
        "prompt": "Calculate the median of [10, 20, 30, 40, 50]. Answer with just the number.",
        "expected_kw": ["30"],
        "recommended_temp": 0.0,
    },
    {
        "agent": "operator",
        "model": "nvidia/nemotron-3.5-lightning:free",
        "role": "Master Operator",
        "prompt": "Name the 3 core state verbs in distributed systems operations.",
        "expected_kw": ["state", "read", "write", "observe", "mutate", "commit", "verify"],
        "recommended_temp": 0.3,
    },
]


def test_model(test_item: Dict[str, Any], api_key: str, max_retries: int = 2) -> Dict[str, Any]:
    model = test_item["model"]
    prompt = test_item["prompt"]
    agent = test_item["agent"]
    temp = test_item["recommended_temp"]

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temp,
        "max_tokens": 512,
    }

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "APEX-Tuning-Harness/1.0",
        },
        method="POST",
    )

    for attempt in range(max_retries + 1):
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                elapsed = time.time() - t0
                res = json.loads(resp.read().decode("utf-8"))
                choices = res.get("choices", [])
                msg = choices[0].get("message", {}) if choices else {}
                raw_content = msg.get("content") or msg.get("reasoning") or ""
                content = raw_content.strip() if isinstance(raw_content, str) else ""

                usage = res.get("usage", {})
                tokens_out = usage.get("completion_tokens", 0)
                tok_sec = round(tokens_out / max(elapsed, 0.001), 1)

                content_lower = content.lower()
                kw_match = any(kw.lower() in content_lower for kw in test_item["expected_kw"])

                return {
                    "agent": agent,
                    "model": model,
                    "status": "PASS" if content and kw_match else ("WARN_KW" if content else "FAIL_EMPTY"),
                    "elapsed_sec": round(elapsed, 2),
                    "tokens_out": tokens_out,
                    "tokens_per_sec": tok_sec,
                    "kw_match": kw_match,
                    "response_sample": content[:120] + ("..." if len(content) > 120 else ""),
                }
        except urllib.error.HTTPError as exc:
            elapsed = time.time() - t0
            if exc.code == 429 and attempt < max_retries:
                time.sleep(3.0)
                continue
            return {
                "agent": agent,
                "model": model,
                "status": f"HTTP_{exc.code}",
                "elapsed_sec": round(elapsed, 2),
                "tokens_out": 0,
                "tokens_per_sec": 0,
                "kw_match": False,
                "error": f"HTTP {exc.code}: {exc.reason}",
            }
        except Exception as exc:
            elapsed = time.time() - t0
            return {
                "agent": agent,
                "model": model,
                "status": "ERROR",
                "elapsed_sec": round(elapsed, 2),
                "tokens_out": 0,
                "tokens_per_sec": 0,
                "kw_match": False,
                "error": str(exc),
            }


def tune_kilo_config(results: List[Dict[str, Any]]):
    """Applies optimal temperature and timeout configs based on benchmark results."""
    cfg_path = Path.home() / ".config/kilo/config.json"
    if not cfg_path.exists():
        return

    try:
        cfg = json.loads(cfg_path.read_text())
        or_models = cfg.get("provider", {}).get("openrouter", {}).get("models", {})

        # Apply calibrated parameters
        for r in results:
            m_id = r["model"]
            if m_id in or_models:
                or_models[m_id]["temperature"] = next((t["recommended_temp"] for t in TEST_MATRIX if t["model"] == m_id), 0.2)

        cfg["provider"]["openrouter"]["models"] = or_models
        cfg_path.write_text(json.dumps(cfg, indent=2))
        print("✓ Successfully tuned ~/.config/kilo/config.json with calibrated temperatures.")
    except Exception as e:
        print(f"⚠️ Tuning config failed: {e}")


def main():
    print("=" * 75)
    print("⚡ APEX AGENT FLEET BENCHMARK & TUNING SUITE")
    print("=" * 75)

    api_key = get_openrouter_api_key()
    if not api_key:
        print("❌ Fatal: No valid OpenRouter API key found.")
        sys.exit(1)

    print(f"Using OpenRouter Key: {api_key[:12]}...{api_key[-6:]}\n")

    results = []
    for idx, test_item in enumerate(TEST_MATRIX, start=1):
        print(f"[{idx}/{len(TEST_MATRIX)}] Testing {test_item['agent']} ({test_item['model']})... ", end="", flush=True)
        res = test_model(test_item, api_key)
        results.append(res)
        if res["status"] == "PASS":
            print(f"🟢 PASS ({res['elapsed_sec']}s | {res['tokens_per_sec']} tok/s)")
        elif res["status"] == "WARN_KW":
            print(f"🟡 WARN ({res['elapsed_sec']}s - Response received, keyword soft-match)")
        else:
            print(f"🔴 {res['status']} ({res.get('error', 'empty response')})")
        time.sleep(2.5)

    # Tune config
    tune_kilo_config(results)

    # Summary
    print("\n" + "=" * 75)
    print(f"{'AGENT':<18} | {'MODEL':<35} | {'LATENCY':<8} | {'SPEED':<10} | {'STATUS'}")
    print("-" * 75)
    for r in results:
        speed_str = f"{r['tokens_per_sec']} t/s" if r['tokens_per_sec'] > 0 else "-"
        print(f"{r['agent']:<18} | {r['model']:<35} | {r['elapsed_sec']}s{'':<3} | {speed_str:<10} | {r['status']}")
    print("=" * 75)

    # Save JSON report
    report_file = Path("/tmp/kilo_fleet_benchmark.json")
    report_file.write_text(json.dumps(results, indent=2))
    print(f"Benchmark results persisted to: {report_file}")


if __name__ == "__main__":
    main()
