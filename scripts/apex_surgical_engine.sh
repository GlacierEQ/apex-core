#!/bin/bash
# APEX SURGICAL ENGINE - Highest Intelligence Synchronization
# Implements the 4-Step Pipeline: Backup, Fetch Override, Surgical Sync, AST Harvest

TARGET_REPO=$1

if [ -z "$TARGET_REPO" ]; then
    echo "Usage: ./apex_surgical_engine.sh /path/to/repo"
    exit 1
fi

cd "$TARGET_REPO" || exit 1
echo "[APEX] Target locked: $TARGET_REPO"

# 1. Hard Backup
echo "[APEX] Step 1: Establishing Pre-AST Hard Backup..."
git branch "main-safe-backup-pre-ast-$(date +%s)"

# 2. Fetch Override
echo "[APEX] Step 2: Bypassing GH Credential Trap and Fetching..."
git -c credential.helper= fetch --all --prune

# 3. Surgical Sync
echo "[APEX] Step 3: Executing Surgical Text Sync..."
cat << 'INNEREOF' > /tmp/safe_surgical_merge.py
import subprocess
import os

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

current_branch = run("git branch --show-current").stdout.strip()
if not current_branch:
    current_branch = "main"

out = run(f"git branch -r --no-merged {current_branch} | grep -v '\\->'")
branches = [b.strip() for b in out.stdout.splitlines() if b.strip()]

success = []
failed = []

# Create patch directory
patch_dir = os.path.join(os.getcwd(), ".apex_aborted_patches")
os.makedirs(patch_dir, exist_ok=True)

for b in branches:
    res = run(f"git merge {b} --no-edit -m 'merge: safe surgical integration of {b}'")
    if res.returncode == 0:
        success.append(b)
    else:
        run("git merge --abort")
        failed.append(b)
        # Generate the exact diff patch for the AI Synthesis Engine
        safe_name = b.replace("/", "_")
        run(f"git diff {current_branch}..{b} > {patch_dir}/{safe_name}.patch")

print(f"--- SURGICAL SYNC RESULTS ---")
print(f"Successfully integrated {len(success)} branches cleanly.")
print(f"Aborted {len(failed)} branches. Generated .patch files in .apex_aborted_patches/ for AI Synthesis.")
INNEREOF
python3 /tmp/safe_surgical_merge.py


# 4. AST Harvest
echo "[APEX] Step 4: Deploying AST Harvester for Rejected Branches..."
python3 /tmp/ast_harvester.py

echo "[APEX] Engine Complete for $TARGET_REPO"
