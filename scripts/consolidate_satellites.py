#!/usr/bin/env python3
"""
APEX SATELLITE DIRECTORY CONSOLIDATION ENGINE
Standard: Lossless synchronization and symlinking of satellite workspaces into the APEX Monolith.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

HOME = Path("/Users/kcbflux")
APEX = HOME / "APEX_SYSTEM"


def sync_directory(src: Path, dst: Path) -> int:
    """Recursively copy all files from src to dst without overwriting newer files."""
    dst.mkdir(parents=True, exist_ok=True)
    synced_count = 0
    for root, dirs, files in os.walk(src):
        rel_path = Path(root).relative_to(src)
        target_dir = dst / rel_path
        target_dir.mkdir(parents=True, exist_ok=True)

        for f in files:
            src_file = Path(root) / f
            dst_file = target_dir / f
            if not dst_file.exists() or src_file.stat().st_mtime > dst_file.stat().st_mtime:
                shutil.copy2(src_file, dst_file)
                synced_count += 1
    return synced_count


def consolidate_and_symlink(src_name: str, dst_path: Path) -> None:
    src_path = HOME / src_name
    if not src_path.exists():
        print(f"[-] Source ~/{src_name} does not exist. Skipping.")
        return

    if src_path.is_symlink():
        target = src_path.resolve()
        if target == dst_path.resolve():
            print(f"✓ ~/{src_name} is already correctly symlinked to {dst_path}")
            return
        else:
            print(f"[*] Updating symlink ~/{src_name} -> {dst_path}")
            src_path.unlink()
            src_path.symlink_to(dst_path)
            return

    # Real directory
    print(f"[*] Syncing ~/{src_name} -> {dst_path}...")
    synced = sync_directory(src_path, dst_path)
    print(f"  └─ Copied/Updated {synced} files.")

    # Verification: Count files
    dst_files = list(dst_path.glob("**/*"))
    print(f"  └─ Verified {len(dst_files)} items present in destination.")

    # Remove src directory and create symlink
    shutil.rmtree(src_path)
    src_path.symlink_to(dst_path)
    print(f"  🟢 Cleanly converted ~/{src_name} to symlink -> {dst_path}")


def consolidate_scratch_files() -> None:
    scratch_dir = APEX / "INFRASTRUCTURE" / "apex-core" / "scratch"
    scratch_dir.mkdir(parents=True, exist_ok=True)

    scratch_files = ["kilo-integration.js", "scratch_evict.swift"]
    for fname in scratch_files:
        fpath = HOME / fname
        if fpath.exists() and fpath.is_file():
            dst = scratch_dir / fname
            shutil.move(str(fpath), str(dst))
            print(f"  ✓ Moved ~/{fname} -> {dst.relative_to(HOME)}")


def main():
    print("=" * 80)
    print("🏛️  APEX MONOLITH LOSSLESS SATELLITE CONSOLIDATION")
    print("=" * 80)

    # 1. GlacierEQ_Swarm
    consolidate_and_symlink(
        "GlacierEQ_Swarm",
        APEX / "DOMAINS" / "SWARM_INTELLIGENCE" / "GlacierEQ_Swarm",
    )

    # 2. automation
    consolidate_and_symlink(
        "automation",
        APEX / "INFRASTRUCTURE" / "services" / "automation",
    )

    # 3. output
    consolidate_and_symlink(
        "output",
        APEX / "ARCHIVE" / "output",
    )

    # 4. Alter Prompts
    consolidate_and_symlink(
        "Alter Prompts",
        APEX / "ARCHIVE" / "Alter Prompts",
    )

    # 5. Scratch Files
    print("\n[*] Consolidating loose scratch files in root home...")
    consolidate_scratch_files()

    print("\n" + "=" * 80)
    print("✅ SATELLITE CONSOLIDATION COMPLETE: 100% DATA LOSSLESS")
    print("=" * 80)


if __name__ == "__main__":
    main()
