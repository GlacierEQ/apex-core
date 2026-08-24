#!/usr/bin/env python3
"""
APEX AUTONOMOUS ESTATE HEALTH DAEMON & DRIFT GUARD
Standard: Continuous monitoring, automated self-healing, and health verification across all estate nodes.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

HEALTH_LOG = Path.home() / ".gemini" / "antigravity-cli" / "apex_daemon_health.log"


class ApexEstateDaemon:
    """
    Continuous drift guard and integrity watchdog.
    """

    @staticmethod
    def run_health_sweep() -> Dict[str, Any]:
        t0 = time.time()
        results = {"timestamp": t0, "checks": {}, "healthy": True}

        # 1. Hardening & Permissions
        p_harden = subprocess.run(
            ["python3", "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts/apex_harden.py"],
            capture_output=True,
            text=True,
        )
        results["checks"]["hardening"] = {
            "passed": p_harden.returncode == 0,
            "exit_code": p_harden.returncode,
        }
        if p_harden.returncode != 0:
            results["healthy"] = False

        # 2. MCP Pools Sync
        p_sync = subprocess.run(
            ["python3", "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts/sync_mcp_pool.py"],
            capture_output=True,
            text=True,
        )
        results["checks"]["mcp_sync"] = {
            "passed": p_sync.returncode == 0,
            "exit_code": p_sync.returncode,
        }
        if p_sync.returncode != 0:
            results["healthy"] = False

        # Log Result
        HEALTH_LOG.parent.mkdir(parents=True, exist_ok=True)
        log_line = f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t0))}] HEALTH: {'🟢 100% OK' if results['healthy'] else '🔴 DRIFT DETECTED'}\n"
        with open(HEALTH_LOG, "a", encoding="utf-8") as f:
            f.write(log_line)

        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="APEX Autonomous Estate Health Daemon")
    parser.add_argument("--loop", action="store_true", help="Run in continuous daemon loop")
    parser.add_argument("--interval", type=int, default=3600, help="Interval in seconds between sweeps")
    args = parser.parse_args()

    if args.loop:
        print(f"[*] Starting APEX Estate Health Daemon (Interval: {args.interval}s)...")
        while True:
            res = ApexEstateDaemon.run_health_sweep()
            print(f"[{time.strftime('%H:%M:%S')}] Health check: {'🟢 OK' if res['healthy'] else '🔴 DRIFT'}")
            time.sleep(args.interval)
    else:
        res = ApexEstateDaemon.run_health_sweep()
        print("=" * 80)
        print(f"🛡️  APEX HEALTH SWEEP RESULT: {'🟢 100% HEALTHY' if res['healthy'] else '🔴 ISSUES DETECTED'}")
        print("=" * 80)
        print(json.dumps(res, indent=2))
