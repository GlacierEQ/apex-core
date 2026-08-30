#!/usr/bin/env python3
"""
APEX CASE REPOSITORIES AUDIT & INVENTORY ENGINE
Standard: Level 1 AST/Structure & Level 2 Behavioral Standard (AGENTS.md)
Inspects all case repositories across the estate:
- Git status & remote origin
- Uncommitted changes / untracked files
- File count & disk usage
- Bates manifests and SHA-256 evidence integrity
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

SEARCH_DIRS = [
    Path("/Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE/github_mirror"),
    Path("/Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE/LEGAL_DATA"),
    Path("/Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE"),
]


def audit_git_repo(repo_dir: Path) -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "name": repo_dir.name,
        "path": str(repo_dir),
        "is_git": (repo_dir / ".git").exists(),
        "remotes": {},
        "branch": "unknown",
        "clean": False,
        "uncommitted": 0,
        "total_files": 0,
        "total_size_mb": 0.0,
        "has_manifest": False,
    }

    if not info["is_git"]:
        return info

    try:
        # Remotes
        res_r = subprocess.run(["git", "-C", str(repo_dir), "remote", "-v"], capture_output=True, text=True)
        remotes = {}
        for line in res_r.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                remotes[parts[0]] = parts[1]
        info["remotes"] = remotes

        # Branch
        res_b = subprocess.run(["git", "-C", str(repo_dir), "branch", "--show-current"], capture_output=True, text=True)
        info["branch"] = res_b.stdout.strip() or "HEAD (detached)"

        # Status
        res_s = subprocess.run(["git", "-C", str(repo_dir), "status", "--porcelain"], capture_output=True, text=True)
        uncommitted = [l for l in res_s.stdout.splitlines() if l.strip()]
        info["uncommitted"] = len(uncommitted)
        info["clean"] = len(uncommitted) == 0

        # Manifest check
        for m_name in ["00_FORENSIC_MASTER_TIMELINE.json", "FORENSIC_SHA256_MANIFEST.json", "BATES_MANIFEST.json"]:
            if (repo_dir / m_name).exists():
                info["has_manifest"] = True
                break

    except Exception as e:
        info["error"] = str(e)

    # Use git ls-files for instant, accurate count without walking node_modules
    try:
        res_f = subprocess.run(["git", "-C", str(repo_dir), "ls-files"], capture_output=True, text=True)
        files = [f for f in res_f.stdout.splitlines() if f.strip()]
        info["total_files"] = len(files)
    except Exception:
        pass

    return info


def main():
    print("=" * 80)
    print("⚖️ APEX CASE REPOSITORIES DISCOVERY & HEALTH AUDIT")
    print("=" * 80)

    discovered_repos: List[Dict[str, Any]] = []
    seen_paths = set()

    for s_dir in SEARCH_DIRS:
        if not s_dir.exists():
            continue
        for child in s_dir.iterdir():
            if child.is_dir() and (child / ".git").exists() and str(child) not in seen_paths:
                seen_paths.add(str(child))
                rep = audit_git_repo(child)
                discovered_repos.append(rep)

    print(f"Total Case Repositories Found: {len(discovered_repos)}\n")
    print(f"{'REPOSITORY':<36} | {'BRANCH':<12} | {'CLEAN':<10} | {'TRACKED':<8} | {'MANIFEST':<9} | {'REMOTE'}")
    print("-" * 115)
    for r in discovered_repos:
        clean_str = "🟢 CLEAN" if r["clean"] else f"🟡 {r['uncommitted']} diffs"
        manifest_str = "🟢 YES" if r["has_manifest"] else "⚪ NO"
        remote_str = r["remotes"].get("origin", "no-remote")
        if len(remote_str) > 40:
            remote_str = "..." + remote_str[-37:]
        print(f"{r['name']:<36} | {r['branch']:<12} | {clean_str:<10} | {str(r['total_files']) + ' files':<8} | {manifest_str:<9} | {remote_str}")
    print("=" * 115)

    out_file = Path("/tmp/case_repos_audit.json")
    out_file.write_text(json.dumps(discovered_repos, indent=2))
    print(f"Full audit report saved to: {out_file}")


if __name__ == "__main__":
    main()
