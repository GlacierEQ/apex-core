#!/usr/bin/env python3
"""
APEX ESTATE PUSHER & SOVEREIGN BRANCH CONSOLIDATOR
Standard: Iterates through local repositories, commits clean changes, and pushes
          to origin main or creates a feature PR if protected by repository rulesets.
"""

import os
import subprocess
import sys
from pathlib import Path

ESTATE_DIR = Path("/Users/kcbflux/APEX_SYSTEM/DOMAINS/PORTFOLIO_ESTATE")

ENV = os.environ.copy()
ENV["GIT_TERMINAL_PROMPT"] = "0"
ENV["PYTHONUNBUFFERED"] = "1"

def get_repos():
    repos = [d for d in ESTATE_DIR.iterdir() if d.is_dir() and (d / ".git").exists()]
    repos.append(Path("/Users/kcbflux/monolith"))
    repos.append(Path("/Users/kcbflux/mega-skills"))
    return sorted(repos, key=lambda p: p.name)

def run_cmd(cmd, cwd, timeout=30):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=ENV)
    except subprocess.TimeoutExpired:
        res = subprocess.CompletedProcess(cmd, 1)
        res.stdout = ""
        res.stderr = "Command timed out after 30s"
        return res

def process_repo(repo: Path):
    print(f"\n[*] Inspecting {repo.name}...", flush=True)
    
    # Check status
    s = run_cmd(["git", "status", "--porcelain"], cwd=repo)
    if not s.stdout.strip():
        # Check if ahead of remote
        ahead = run_cmd(["git", "rev-list", "@{u}..HEAD"], cwd=repo)
        if ahead.returncode == 0 and ahead.stdout.strip():
            print(f"  └─ Unpushed commits detected. Pushing...", flush=True)
            push_res = run_cmd(["git", "push", "origin", "HEAD"], cwd=repo)
            if push_res.returncode == 0:
                print(f"  ✓ Pushed successfully to origin!", flush=True)
            else:
                print(f"  ⚠️ Direct push failed: {push_res.stderr.strip()[:200]}", flush=True)
        else:
            print(f"  ✓ Clean and up to date.", flush=True)
        return

    print(f"  └─ Dirty tree ({len(s.stdout.splitlines())} files). Staging changes...", flush=True)
    run_cmd(["git", "add", "-A"], cwd=repo)
    
    commit_res = run_cmd(["git", "commit", "-m", "chore(apex): estate alignment and sovereign capability consolidation"], cwd=repo)
    if commit_res.returncode != 0:
        print(f"  ⚠️ Commit failed: {commit_res.stderr.strip()[:200]}", flush=True)
        return

    print(f"  └─ Committed. Attempting push to origin...", flush=True)
    curr_branch = run_cmd(["git", "branch", "--show-current"], cwd=repo).stdout.strip() or "main"
    
    push_res = run_cmd(["git", "push", "origin", curr_branch], cwd=repo)
    if push_res.returncode == 0:
        print(f"  ✓ Successfully pushed {curr_branch} to origin!", flush=True)
        return

    # If push failed because of branch protection / rule violations
    err = push_res.stderr.lower()
    if "rule violations" in err or "protected" in err or "pull request" in err or "declined" in err:
        print(f"  ℹ️ Repository ruleset requires a Pull Request. Creating branch feat/apex-alignment...", flush=True)
        run_cmd(["git", "checkout", "-B", "feat/apex-alignment"], cwd=repo)
        branch_push = run_cmd(["git", "push", "-u", "origin", "feat/apex-alignment"], cwd=repo)
        if branch_push.returncode == 0:
            print(f"  ✓ Pushed branch feat/apex-alignment to origin. Creating PR...", flush=True)
            pr_res = run_cmd([
                "gh", "pr", "create",
                "--title", "chore(apex): estate alignment and sovereign capability consolidation",
                "--body", "Automated APEX Sovereign alignment across estate codebase.",
                "--head", "feat/apex-alignment"
            ], cwd=repo)
            if pr_res.returncode == 0:
                print(f"  ✓ PR Created: {pr_res.stdout.strip()}", flush=True)
            else:
                print(f"  ⚠️ PR creation note: {pr_res.stderr.strip()[:200]}", flush=True)
        else:
            print(f"  ⚠️ Branch push failed: {branch_push.stderr.strip()[:200]}", flush=True)
    else:
        print(f"  ⚠️ Push failed: {push_res.stderr.strip()[:200]}", flush=True)

def main():
    repos = get_repos()
    print(f"================================================================================", flush=True)
    print(f"🏛️ APEX SOVEREIGN ESTATE PUSHER ({len(repos)} Repositories)", flush=True)
    print(f"================================================================================", flush=True)
    for r in repos:
        process_repo(r)

if __name__ == "__main__":
    main()
