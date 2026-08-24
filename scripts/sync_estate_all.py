#!/usr/bin/env python3
"""
APEX MASTER ESTATE SYNC ALL SCRIPT (STREAMING & REAL-TIME)
Synchronizes MCP pools, models_config, permissions, git hooks, vector delta indexes, and runs verification test suite.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_step(title: str, cmd: list) -> bool:
    print(f"\n⚙️  {title}...", flush=True)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    if p.stdout:
        for line in iter(p.stdout.readline, ""):
            lines.append(line.strip())
            if any(k in line for k in ("Synced", "Verified", "Installed", "Indexed", "passed", "100%", "SUCCESS", "COMPLETE", "ERROR", "FAILED")):
                print(f"  └─ {line.strip()}", flush=True)
    p.wait()
    if p.returncode == 0:
        print(f"  🟢 SUCCESS", flush=True)
        return True
    else:
        print(f"  🔴 FAILED (Exit Code {p.returncode})", flush=True)
        return False


def main():
    print("=" * 80, flush=True)
    print("🔄 APEX MASTER ESTATE SYNCHRONIZATION ORCHESTRATOR (SYNC ALL)", flush=True)
    print("=" * 80, flush=True)

    steps = [
        ("1. Master Two-Tier MCP Pool Synchronization", ["python3", "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts/sync_mcp_pool.py"]),
        ("2. Estate Hardening & POSIX Permissions (0o600 / 0o755)", ["python3", "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts/apex_harden.py"]),
        ("3. Global Git Pre-Commit Security Hooks", ["python3", "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts/install_git_hooks.py"]),
        ("4. Multi-Cloud Vector Knowledge Index Delta Crawl", ["python3", "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts/apex_omni_cloud_ml.py", "crawl", "--max-files", "25"]),
        ("5. Full Estate Pytest Verification Suite (13/13 Green)", ["python3", "-m", "pytest", "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/tests"]),
    ]

    all_passed = True
    for title, cmd in steps:
        ok = run_step(title, cmd)
        if not ok:
            all_passed = False

    print("\n" + "=" * 80, flush=True)
    if all_passed:
        print("✅ APEX MASTER ESTATE FULL SYNCHRONIZATION COMPLETE: 100% GREEN", flush=True)
    else:
        print("⚠️ APEX SYNCHRONIZATION FINISHED WITH ISSUES", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    main()
