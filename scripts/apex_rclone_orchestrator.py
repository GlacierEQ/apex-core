#!/usr/bin/env python3
"""
APEX Rclone Multi-Cloud Storage Orchestrator
Standard: Level 3 Colossal Backend & Multi-Cloud Horizon Sync
Coordinates bidirectional delta-syncing, cryptographic checksum auditing, and offline archiving
between Local APEX, ShadowDrive (4.0TB APFS external), and Google Drive (gdrive:).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

SHADOWDRIVE_PATH = Path("/Volumes/ShadowDrive")
LOCAL_APEX_PATH = Path("/Users/kcbflux/APEX_SYSTEM")
RCLONE_CONFIG_PATH = Path.home() / ".config/rclone/rclone.conf"
REPORT_PATH = SHADOWDRIVE_PATH / "RCLONE_SYNC_MANIFEST.json"


class ApexRcloneOrchestrator:
    """Universal controller for Rclone multi-cloud operations across APEX horizons."""

    def __init__(self, rclone_bin: str = "rclone"):
        self.rclone_bin = shutil.which(rclone_bin) or "/usr/local/bin/rclone"
        self.shadow_mount = SHADOWDRIVE_PATH
        self.local_apex = LOCAL_APEX_PATH

    def is_rclone_available(self) -> bool:
        return Path(self.rclone_bin).exists() and os.access(self.rclone_bin, os.X_OK)

    def is_shadowdrive_mounted(self) -> bool:
        return self.shadow_mount.exists() and self.shadow_mount.is_dir()

    def get_configured_remotes(self) -> List[str]:
        if not self.is_rclone_available():
            return []
        try:
            res = subprocess.run(
                [self.rclone_bin, "listremotes"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            return [line.strip() for line in res.stdout.splitlines() if line.strip()]
        except Exception:
            return []

    def inspect_horizon_status(self) -> Dict[str, Any]:
        """Audits the connectivity and storage health of all three horizons."""
        status = {
            "timestamp_utc": time.time(),
            "rclone_installed": self.is_rclone_available(),
            "rclone_path": self.rclone_bin,
            "remotes": self.get_configured_remotes(),
            "horizons": {
                "local_apex": {
                    "path": str(self.local_apex),
                    "exists": self.local_apex.exists(),
                },
                "shadowdrive": {
                    "path": str(self.shadow_mount),
                    "mounted": self.is_shadowdrive_mounted(),
                    "free_bytes": 0,
                    "total_bytes": 0,
                },
                "gdrive": {
                    "configured": "gdrive:" in self.get_configured_remotes(),
                    "accessible": False,
                    "root_folders": [],
                },
            },
        }

        # Inspect ShadowDrive disk usage if mounted
        if self.is_shadowdrive_mounted():
            try:
                usage = shutil.disk_usage(self.shadow_mount)
                status["horizons"]["shadowdrive"]["free_bytes"] = usage.free
                status["horizons"]["shadowdrive"]["total_bytes"] = usage.total
                status["horizons"]["shadowdrive"]["free_gb"] = round(usage.free / (1024**3), 2)
            except Exception as e:
                status["horizons"]["shadowdrive"]["error"] = str(e)

        # Inspect Google Drive if configured
        if status["horizons"]["gdrive"]["configured"]:
            try:
                res = subprocess.run(
                    [self.rclone_bin, "lsd", "gdrive:", "--max-depth", "1"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10,
                )
                if res.returncode == 0:
                    status["horizons"]["gdrive"]["accessible"] = True
                    folders = []
                    for line in res.stdout.splitlines():
                        parts = line.strip().split()
                        if parts:
                            folders.append(parts[-1])
                    status["horizons"]["gdrive"]["root_folders"] = folders
            except Exception as e:
                status["horizons"]["gdrive"]["error"] = str(e)

        return status

    def sync_path(
        self,
        source: str,
        destination: str,
        dry_run: bool = False,
        checksum: bool = True,
        transfers: int = 4,
        checkers: int = 8,
    ) -> Dict[str, Any]:
        """
        Executes a deterministic delta-sync between any two horizons.
        Supports local-to-cloud, cloud-to-local, or cloud-to-external-drive.
        """
        if not self.is_rclone_available():
            raise RuntimeError(f"Rclone binary not found at {self.rclone_bin}")

        cmd = [
            self.rclone_bin,
            "sync",
            source,
            destination,
            f"--transfers={transfers}",
            f"--checkers={checkers}",
            "--fast-list",
            "--stats=5s",
        ]

        if checksum:
            cmd.append("--checksum")
        if dry_run:
            cmd.append("--dry-run")

        t0 = time.time()
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        duration = time.time() - t0

        return {
            "source": source,
            "destination": destination,
            "success": process.returncode == 0,
            "exit_code": process.returncode,
            "duration_seconds": round(duration, 3),
            "dry_run": dry_run,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }

    def check_integrity(self, source: str, destination: str) -> Dict[str, Any]:
        """Cryptographically verifies that source and destination match bit-for-bit."""
        cmd = [
            self.rclone_bin,
            "check",
            source,
            destination,
            "--one-way",
            "--fast-list",
        ]
        t0 = time.time()
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        duration = time.time() - t0

        return {
            "source": source,
            "destination": destination,
            "matches": process.returncode == 0,
            "exit_code": process.returncode,
            "duration_seconds": round(duration, 3),
            "output": process.stderr or process.stdout,
        }


def print_status_table(status: Dict[str, Any]):
    print("=" * 80)
    print("🌐 APEX RClone Multi-Cloud Horizon Status")
    print("=" * 80)
    rclone_ok = status.get("rclone_installed", False)
    print(f"Rclone Engine        : {'🟢 ACTIVE' if rclone_ok else '🔴 MISSING'} ({status.get('rclone_path')})")
    print(f"Configured Remotes   : {', '.join(status.get('remotes', [])) or 'None'}")

    h = status.get("horizons", {})
    # Local
    loc = h.get("local_apex", {})
    print(f"Horizon 1 (Local SSD): {'🟢 ONLINE' if loc.get('exists') else '🔴 OFFLINE'} -> {loc.get('path')}")

    # ShadowDrive
    sd = h.get("shadowdrive", {})
    sd_mounted = sd.get("mounted", False)
    sd_free = sd.get("free_gb", 0)
    print(f"Horizon 2 (ShadowDrive): {'🟢 MOUNTED' if sd_mounted else '🔴 DISCONNECTED'} -> {sd.get('path')} ({sd_free} GB Free)")

    # GDrive
    gd = h.get("gdrive", {})
    gd_ok = gd.get("accessible", False)
    folders = ", ".join(gd.get("root_folders", []))
    print(f"Horizon 3 (Google Drive): {'🟢 CONNECTED' if gd_ok else '🔴 DISCONNECTED'} -> Folders: [{folders}]")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="APEX Rclone Multi-Cloud Storage Orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Operational command")

    # status
    subparsers.add_parser("status", help="Inspect connectivity and storage across all cloud horizons")

    # sync-evidence
    p_ev = subparsers.add_parser("sync-evidence", help="Sync legal case evidence from Google Drive to ShadowDrive")
    p_ev.add_argument("--dry-run", action="store_true", help="Perform trial run without copying files")

    # sync-backups
    p_bk = subparsers.add_parser("sync-backups", help="Mirror APEX backups from Google Drive to ShadowDrive")
    p_bk.add_argument("--dry-run", action="store_true", help="Perform trial run without copying files")

    # backup-to-cloud
    p_up = subparsers.add_parser("backup-manifests", help="Backup local forensic manifests & timelines to Google Drive")
    p_up.add_argument("--dry-run", action="store_true", help="Perform trial run without copying files")

    args = parser.parse_args()
    orchestrator = ApexRcloneOrchestrator()

    if args.command == "status" or not args.command:
        stat = orchestrator.inspect_horizon_status()
        print_status_table(stat)
        sys.exit(0)

    elif args.command == "sync-evidence":
        if not orchestrator.is_shadowdrive_mounted():
            print("❌ Error: ShadowDrive (/Volumes/ShadowDrive) is not mounted. Plug it in to proceed.", file=sys.stderr)
            sys.exit(1)
        dest = str(SHADOWDRIVE_PATH / "01_LEGAL_EVIDENCE_VAULT/gdrive_case_mirror")
        print(f"🔄 Syncing gdrive:00_CASE_CONTROL_CENTER -> {dest} (dry_run={args.dry_run})...")
        res = orchestrator.sync_path("gdrive:00_CASE_CONTROL_CENTER", dest, dry_run=args.dry_run)
        print(f"Result: {'🟢 SUCCESS' if res['success'] else '🔴 FAILED'} in {res['duration_seconds']}s")
        if res["stderr"]:
            print(res["stderr"])
        sys.exit(res["exit_code"])

    elif args.command == "sync-backups":
        if not orchestrator.is_shadowdrive_mounted():
            print("❌ Error: ShadowDrive (/Volumes/ShadowDrive) is not mounted. Plug it in to proceed.", file=sys.stderr)
            sys.exit(1)
        dest = str(SHADOWDRIVE_PATH / "APEX_ARCHIVES/gdrive_backups")
        print(f"🔄 Syncing gdrive:APEX_BACKUPS -> {dest} (dry_run={args.dry_run})...")
        res = orchestrator.sync_path("gdrive:APEX_BACKUPS", dest, dry_run=args.dry_run)
        print(f"Result: {'🟢 SUCCESS' if res['success'] else '🔴 FAILED'} in {res['duration_seconds']}s")
        if res["stderr"]:
            print(res["stderr"])
        sys.exit(res["exit_code"])

    elif args.command == "backup-manifests":
        src = "/Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE/LEGAL_DATA/CYBERTACK-1FDV-23-0001009"
        dest = "gdrive:00_CASE_CONTROL_CENTER/00_FORENSIC_SNAPSHOTS"
        print(f"🔄 Uploading local forensic timeline & manifests -> {dest} (dry_run={args.dry_run})...")
        res = orchestrator.sync_path(src, dest, dry_run=args.dry_run)
        print(f"Result: {'🟢 SUCCESS' if res['success'] else '🔴 FAILED'} in {res['duration_seconds']}s")
        if res["stderr"]:
            print(res["stderr"])
        sys.exit(res["exit_code"])


if __name__ == "__main__":
    main()
