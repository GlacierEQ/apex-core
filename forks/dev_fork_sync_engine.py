#!/usr/bin/env python3
"""
APEX DEV FORK DOCTRINE ORCHESTRATOR & UPSTREAM SYNC ENGINE
Standard: Non-Destructive Overlay Pattern & Clean Upstream Tracking
Managed Forks: antigravity-cli, OpenCode, Kilo, Whisper.cpp, etc.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any

MANAGED_FORKS = [
    {"name": "antigravity-cli", "path": Path("/Users/kcbflux/antigravity-cli"), "upstream_remote": "upstream", "overlay_dir": "extensions"},
    {"name": "mega-skills", "path": Path("/Users/kcbflux/mega-skills"), "upstream_remote": "origin", "overlay_dir": "skills"},
    {"name": "monolith", "path": Path("/Users/kcbflux/monolith"), "upstream_remote": "origin", "overlay_dir": "overlay"},
]


class DevForkSyncEngine:
    def __init__(self):
        self.forks = MANAGED_FORKS

    def audit_forks(self) -> List[Dict[str, Any]]:
        results = []
        for fork in self.forks:
            p = fork["path"]
            exists = p.exists() and (p / ".git").exists()
            clean_tree = False
            current_branch = "unknown"
            
            if exists:
                try:
                    res_branch = subprocess.run(["git", "-C", str(p), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
                    current_branch = res_branch.stdout.strip()
                    res_status = subprocess.run(["git", "-C", str(p), "status", "--porcelain"], capture_output=True, text=True)
                    clean_tree = len(res_status.stdout.strip()) == 0
                except Exception:
                    pass

            results.append({
                "fork_name": fork["name"],
                "path": str(p),
                "is_git_repository": exists,
                "current_branch": current_branch,
                "working_tree_clean": clean_tree,
                "overlay_pattern_enforced": (p / fork["overlay_dir"]).exists() if exists else False,
                "status": "HEALTHY_DEV_FORK" if (exists and clean_tree) else "NEEDS_SYNC_OR_UNTRACKED",
            })
        return results

    def get_summary(self) -> Dict[str, Any]:
        audits = self.audit_forks()
        return {
            "doctrine": "APEX Dev Fork Overlay Standard",
            "total_managed_forks": len(self.forks),
            "audits": audits,
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }


def main():
    parser = argparse.ArgumentParser(description="APEX Dev Fork Synchronizer")
    parser.add_argument("--audit", action="store_true", default=True, help="Audit managed dev forks")
    args = parser.parse_args()

    engine = DevForkSyncEngine()
    print("=" * 80)
    print("🔱 APEX DEV FORK DOCTRINE & UPSTREAM SYNCHRONIZER")
    print("=" * 80)
    res = engine.get_summary()
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
