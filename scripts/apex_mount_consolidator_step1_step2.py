#!/usr/bin/env python3
"""
APEX MOUNT CONSOLIDATION & DEDUPLICATION ENGINE (STEPS 1 & 2)
Standard: L2 Cryptographic Proof (Double Helix Invariant)
Features:
  - Multi-process parallelized SHA-256 hashing across all 6 cloud horizons (8MB chunked I/O).
  - 5-Family Taxonomy mapping to /Users/kcbflux/ShadowDrive_Live/.
  - Exact SHA-256 hash intersection and deduplication.
  - Name-collision / hash-divergence resolution (mtime priority + ISO timestamp archival).
  - Rule of Authority priority tie-breaking:
      GlacierEQ (1) > Dropbox (2) > OneDrive (3) > Google Drive (4) > TeraBox (5) > Higuy (6)
  - Exports absolute source manifests, migration ledger, and execution plan.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Canonical Target Root
CANONICAL_TARGET_ROOT = Path("/Users/kcbflux/ShadowDrive_Live").resolve()

# Authority Priority Ranking (Lower value = higher priority)
HORIZON_PRIORITY = {
    "GlacierEQ_GoogleDrive": 1,
    "Dropbox_Mermicor": 2,
    "OneDrive": 3,
    "GoogleDrive": 4,
    "TeraBox": 5,
    "Higuy_GoogleDrive": 6,
}

# 6 Horizon Root Definitions
HORIZON_SOURCES = [
    {
        "horizon_id": "Dropbox_Mermicor",
        "root_path": Path("/Users/kcbflux/Dropbox-Cyber.lazer.mermicor/Cherry Chan"),
    },
    {
        "horizon_id": "GlacierEQ_GoogleDrive",
        "root_path": Path("/Users/kcbflux/glacier.equilibrium@gmail.com - Google Drive/My Drive"),
    },
    {
        "horizon_id": "OneDrive",
        "root_path": Path("/Users/kcbflux/OneDrive"),
    },
    {
        "horizon_id": "GoogleDrive",
        "root_path": Path("/Users/kcbflux/Google Drive"),
    },
    {
        "horizon_id": "TeraBox",
        "root_path": Path("/Users/kcbflux/TeraBox"),
    },
    {
        "horizon_id": "Higuy_GoogleDrive",
        "root_path": Path("/Users/kcbflux/higuy.vids@gmail.com - Google Drive/My Drive"),
    },
]

# Taxonomy Classification Rules
TAXONOMY_RULES = [
    # Family I: LEGAL_DATA
    {
        "family": "LEGAL_DATA",
        "target_prefix": "DOMAINS/LEGAL_WARFARE",
        "patterns": [
            "01_LEGAL_EVIDENTIARY_VAULT",
            "00_CASE_CONTROL_CENTER",
            "01_LEGAL_AND_CASE_WARFARE",
            "02_EVIDENCE_VAULT",
            "01_CASE_PORTFOLIO",
            "03_LEGAL_RESEARCH",
            "04_FORENSIC_ANALYSIS",
            "PACTfvc61324",
            "Legal Library",
            "Divorce",
        ],
    },
    # Family II: SWARM_DATA
    {
        "family": "SWARM_DATA",
        "target_prefix": "DOMAINS/SWARM_INTELLIGENCE",
        "patterns": [
            "05_AI_CONVERSATION_EXPORTS",
            "06_SYSTEM_TELEMETRY_AND_BACKUPS",
            "05_AI_SYSTEM_AND_TOOLS",
            "05_SYSTEM_AND_MEMORY",
            "conversations.json",
            "GlacierEQ_Swarm",
        ],
    },
    # Family III: RUNTIMES_DATA
    {
        "family": "RUNTIMES_DATA",
        "target_prefix": "INFRASTRUCTURE/RUNTIMES",
        "patterns": [
            "02_DEVELOPMENT_AND_REPOS",
            "02_DEV_REPOS_AND_CODE",
            "04_FORENSIC_TRIAGE_AND_SHADOWDRIVE",
            "build",
            "dist",
            "node_modules",
            "Colab Notebooks",
        ],
    },
    # Family IV: ML_DATA
    {
        "family": "ML_DATA",
        "target_prefix": "ENGINES/ML_INTELLIGENCE",
        "patterns": [
            "00_DROPBOX_COMPLETE_FORENSIC_INDEX.json",
            "00_DROPBOX_MASTER_FORENSIC_MANIFEST.json",
            "APEX_ML_TELEMETRY.json",
            "Google AI Studio",
        ],
    },
    # Family V: CLOUD_HORIZONS
    {
        "family": "CLOUD_HORIZONS",
        "target_prefix": "ARCHIVE",
        "patterns": [
            "02_GOOGLE_TAKEOUT_MASTER_ARCHIVES",
            "03_CAMERA_UPLOADS_MEDIA_TIMELINE",
            "03_PERSONAL_ADMIN",
            "03_PERSONAL_AND_TAX_ADMIN",
            "04_MEDIA_VAULT",
            "04_MEDIA_AND_HEARINGS",
            "06_ARCHIVE_STORAGE",
            "06_ARCHIVE_AND_HISTORICAL_VAULT",
            "Camera uploads",
            "Iphotos",
        ],
    },
]

IGNORED_NAMES = {".DS_Store", "Icon\r", ".localized", "desktop.ini", "Thumbs.db"}
CHUNK_SIZE = 8 * 1024 * 1024  # 8MB chunked I/O


@dataclass
class FileRecord:
    source_path: str
    horizon_id: str
    rel_path: str
    size_bytes: int
    mtime_epoch: float
    mtime_iso: str
    sha256: str
    family: str
    target_rel_path: str
    priority: int


def compute_sha256_single(file_path_str: str) -> Optional[Tuple[str, int, float, str, str]]:
    """Worker function: Computes SHA-256 with 8MB streaming buffer."""
    p = Path(file_path_str)
    try:
        if not p.is_file() or p.is_symlink():
            return None
        stat = p.stat()
        size = stat.st_size
        mtime = stat.st_mtime
        mtime_iso = datetime.datetime.fromtimestamp(mtime, tz=datetime.timezone.utc).isoformat()
        
        hasher = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                hasher.update(chunk)
        return (file_path_str, size, mtime, mtime_iso, hasher.hexdigest())
    except (PermissionError, FileNotFoundError, OSError):
        return None


def classify_file(rel_path_str: str) -> Tuple[str, str]:
    """Classifies a relative path into 5-Family Taxonomy."""
    for rule in TAXONOMY_RULES:
        for pat in rule["patterns"]:
            if pat in rel_path_str:
                # Relative path trimmed of top pattern if nested
                clean_rel = rel_path_str.lstrip("/")
                target_rel = f"{rule['target_prefix']}/{clean_rel}"
                return rule["family"], target_rel
    
    # Fallback to Family V / Miscellaneous Archive
    return "CLOUD_HORIZONS", f"ARCHIVE/MISC_UNCATALOGED/{rel_path_str.lstrip('/')}"


def scan_horizon_files(horizon: Dict[str, Any]) -> List[Tuple[str, str, str, int]]:
    """Discovers all candidate files in a horizon root."""
    horizon_id = horizon["horizon_id"]
    root = horizon["root_path"]
    results = []
    if not root.exists():
        return results

    priority = HORIZON_PRIORITY.get(horizon_id, 99)
    for entry in root.rglob("*"):
        if entry.is_file() and not entry.is_symlink():
            if entry.name in IGNORED_NAMES or entry.name.startswith("._") or "/.Trash/" in str(entry):
                continue
            try:
                rel = str(entry.relative_to(root))
                results.append((str(entry), horizon_id, rel, priority))
            except ValueError:
                continue
    return results


def run_parallel_hashing(max_workers: Optional[int] = None) -> List[FileRecord]:
    """Step 1: Scans and hashes all source horizons in parallel."""
    print("=" * 80)
    print("⚡ APEX MOUNT CONSOLIDATION — STEP 1: PARALLEL CRYPTOGRAPHIC HASHING")
    print(f"Workers allocated: {max_workers or os.cpu_count() or 8}")
    print("=" * 80)

    start_scan = time.time()
    all_candidates: List[Tuple[str, str, str, int]] = []
    
    for h in HORIZON_SOURCES:
        h_files = scan_horizon_files(h)
        print(f"  📁 Discovered in {h['horizon_id']:<24}: {len(h_files):>6} files")
        all_candidates.extend(h_files)

    print(f"Total Candidate Files across 6 horizons: {len(all_candidates)}")
    print("Computing cryptographic SHA-256 digests in parallel...")

    file_map: Dict[str, Tuple[str, str, int]] = {
        item[0]: (item[1], item[2], item[3]) for item in all_candidates
    }
    
    records: List[FileRecord] = []
    processed_count = 0
    total_bytes = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(compute_sha256_single, f_path): f_path for f_path in file_map}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            processed_count += 1
            if res is not None:
                f_path, size, mtime, mtime_iso, digest = res
                h_id, rel_path, prio = file_map[f_path]
                family, target_rel = classify_file(rel_path)
                
                records.append(
                    FileRecord(
                        source_path=f_path,
                        horizon_id=h_id,
                        rel_path=rel_path,
                        size_bytes=size,
                        mtime_epoch=mtime,
                        mtime_iso=mtime_iso,
                        sha256=digest,
                        family=family,
                        target_rel_path=target_rel,
                        priority=prio,
                    )
                )
                total_bytes += size

            if processed_count % 1000 == 0 or processed_count == len(all_candidates):
                print(f"  ✓ Hashed {processed_count}/{len(all_candidates)} files ({(total_bytes / (1024**3)):.2f} GB processed)...")

    duration = time.time() - start_scan
    print(f"\n✨ Step 1 Complete in {duration:.2f}s | Hashed: {len(records)} files | Total Volume: {(total_bytes / (1024**3)):.2f} GB")
    return records


def run_cross_manifest_intersection(records: List[FileRecord], output_dir: Path) -> Dict[str, Any]:
    """Step 2: Cross-Manifest Hash Intersection & Deduplication Matrix."""
    print("\n" + "=" * 80)
    print("🧬 APEX MOUNT CONSOLIDATION — STEP 2: CROSS-MANIFEST HASH INTERSECTION")
    print("=" * 80)

    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Group records by SHA-256
    hash_groups: Dict[str, List[FileRecord]] = {}
    for r in records:
        hash_groups.setdefault(r.sha256, []).append(r)

    unique_hashes = len(hash_groups)
    print(f"Total Unique Cryptographic Hashes: {unique_hashes}")

    canonical_actions: List[Dict[str, Any]] = []
    dedup_unlinks: List[Dict[str, Any]] = []
    collision_resolutions: List[Dict[str, Any]] = []
    
    occupied_target_paths: Dict[str, Tuple[str, float]] = {}  # target_rel_path -> (sha256, mtime_epoch)
    saved_bytes = 0

    for sha, group in hash_groups.items():
        # Sort group by Priority (Ascending: 1 is best) then by mtime (Descending: newest first)
        group.sort(key=lambda x: (x.priority, -x.mtime_epoch))
        winner = group[0]
        duplicates = group[1:]

        # Check target path collision with different hash
        target_path = winner.target_rel_path
        if target_path in occupied_target_paths:
            prev_sha, prev_mtime = occupied_target_paths[target_path]
            if prev_sha != sha:
                # Name collision with hash divergence: Rule of Timestamp + Rule of Archival
                if winner.mtime_epoch < prev_mtime:
                    # Current file is older: archive it with timestamp suffix
                    ts_tag = winner.mtime_iso.split("T")[0]
                    p = Path(target_path)
                    archived_name = f"{p.stem}_{ts_tag}{p.suffix}"
                    target_path = f"ARCHIVE/Codex/{winner.family}/{archived_name}"
                    collision_resolutions.append({
                        "original_target": winner.target_rel_path,
                        "archived_target": target_path,
                        "source": winner.source_path,
                        "reason": "Name collision - older version redirected to ARCHIVE/Codex"
                    })
                else:
                    occupied_target_paths[target_path] = (sha, winner.mtime_epoch)
        else:
            occupied_target_paths[target_path] = (sha, winner.mtime_epoch)

        # Plan Winner Migration
        canonical_actions.append({
            "action": "ATOMIC_COPY_VERIFY",
            "source_path": winner.source_path,
            "target_path": str(CANONICAL_TARGET_ROOT / target_path),
            "target_rel_path": target_path,
            "sha256": sha,
            "size_bytes": winner.size_bytes,
            "mtime_epoch": winner.mtime_epoch,
            "mtime_iso": winner.mtime_iso,
            "horizon_id": winner.horizon_id,
            "family": winner.family,
        })

        # Plan Deduplication Unlinks for identical duplicates
        for dup in duplicates:
            saved_bytes += dup.size_bytes
            dedup_unlinks.append({
                "action": "DEDUPLICATE_UNLINK",
                "source_path": dup.source_path,
                "identical_to_canonical": winner.source_path,
                "target_canonical_path": str(CANONICAL_TARGET_ROOT / target_path),
                "sha256": sha,
                "size_bytes": dup.size_bytes,
                "horizon_id": dup.horizon_id,
            })

    # Summary Statistics
    summary = {
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "canonical_root": str(CANONICAL_TARGET_ROOT),
        "total_source_files": len(records),
        "unique_payload_count": unique_hashes,
        "duplicate_files_to_prune": len(dedup_unlinks),
        "redundant_volume_saved_gb": round(saved_bytes / (1024**3), 3),
        "name_collisions_resolved": len(collision_resolutions),
        "family_breakdown": {
            f["family"]: len([a for a in canonical_actions if a["family"] == f["family"]])
            for f in TAXONOMY_RULES
        },
    }

    # Write Manifests & Execution Matrices
    matrix_file = output_dir / "STEP2_DEDUPLICATION_MATRIX.json"
    matrix_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    plan_file = output_dir / "STEP2_MIGRATION_PLAN.jsonl"
    with open(plan_file, "w", encoding="utf-8") as f:
        for act in canonical_actions:
            f.write(json.dumps(act) + "\n")
        for act in dedup_unlinks:
            f.write(json.dumps(act) + "\n")

    print(f"📊 SUMMARY TELEMETRY:")
    print(f"  • Total Source Files Scanned : {len(records)}")
    print(f"  • Unique Cryptographic Files  : {unique_hashes}")
    print(f"  • Redundant Files Deduplicated: {len(dedup_unlinks)}")
    print(f"  • Storage Reclaimed           : {summary['redundant_volume_saved_gb']} GB")
    print(f"  • Hash Divergences Archived   : {len(collision_resolutions)}")
    print(f"  • Migration Plan Saved To     : {plan_file}")
    print(f"  • Matrix Summary Summary Saved To     : {matrix_file}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="APEX Mount Consolidation Steps 1 & 2")
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 8, help="Number of parallel worker processes")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/Users/kcbflux/ShadowDrive_Live/.manifests"),
        help="Directory to save execution manifests and plans",
    )
    args = parser.parse_args()

    records = run_parallel_hashing(max_workers=args.workers)
    run_cross_manifest_intersection(records, args.output_dir)


if __name__ == "__main__":
    main()
