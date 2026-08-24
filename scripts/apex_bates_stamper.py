#!/usr/bin/env python3
"""
APEX FORENSIC BATES STAMPING & PROVENANCE COMPILER
Standard: Legal Bates numbering, SHA-256 cryptographic provenance hashing, and chain-of-custody manifest generation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class BatesExhibit:
    bates_number: str
    original_path: str
    stamped_path: str
    sha256_hash: str
    file_size_bytes: int
    stamped_at_utc: float = field(default_factory=time.time)


class ApexBatesStamper:
    """
    Automates Bates stamping and evidentiary chain-of-custody logging.
    """

    @staticmethod
    def compute_sha256(filepath: Path) -> str:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    @classmethod
    def stamp_collection(
        cls,
        input_dir: Path,
        output_dir: Path,
        prefix: str = "CYBER-",
        start_number: int = 1,
        digits: int = 6,
    ) -> Dict[str, Any]:
        in_p = Path(input_dir).resolve()
        out_p = Path(output_dir).resolve()
        out_p.mkdir(parents=True, exist_ok=True)

        files = sorted([f for f in in_p.glob("**/*") if f.is_file() and not f.name.startswith(".")])
        manifest_exhibits: List[BatesExhibit] = []

        print("=" * 80)
        print("🏛️  APEX FORENSIC BATES STAMPING & PROVENANCE COMPILER")
        print(f"Source Directory : {in_p}")
        print(f"Output Directory : {out_p}")
        print(f"Bates Prefix     : {prefix}")
        print(f"Total Exhibits   : {len(files)}")
        print("=" * 80)

        current_idx = start_number
        for f in files:
            bates_id = f"{prefix}{current_idx:0{digits}d}"
            target_name = f"{bates_id}_{f.name}"
            target_path = out_p / target_name

            # Copy file
            shutil.copy2(f, target_path)
            f_hash = cls.compute_sha256(target_path)
            f_size = target_path.stat().st_size

            exhibit = BatesExhibit(
                bates_number=bates_id,
                original_path=str(f),
                stamped_path=str(target_path),
                sha256_hash=f_hash,
                file_size_bytes=f_size,
            )
            manifest_exhibits.append(exhibit)
            print(f"  ✓ [{bates_id}] {f.name} -> SHA256: {f_hash[:16]}...")
            current_idx += 1

        # Write Manifests
        manifest_data = {
            "title": f"Bates Provenance & Chain of Custody Manifest ({prefix})",
            "compiled_at_utc": time.time(),
            "prefix": prefix,
            "total_items": len(manifest_exhibits),
            "exhibits": [asdict(e) for e in manifest_exhibits],
        }
        json_manifest = out_p / "BATES_MANIFEST.json"
        json_manifest.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

        # Markdown Manifest for Court Pleadings
        md_lines = [
            f"# EXHIBIT & BATES STAMP INDEX: {prefix}",
            f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
            f"**Total Exhibits**: {len(manifest_exhibits)}",
            "",
            "| Bates No. | Original File | Size (Bytes) | SHA-256 Cryptographic Hash |",
            "|---|---|---|---|",
        ]
        for e in manifest_exhibits:
            md_lines.append(f"| **{e.bates_number}** | `{Path(e.original_path).name}` | {e.file_size_bytes:,} | `{e.sha256_hash}` |")

        md_manifest = out_p / "BATES_INDEX.md"
        md_manifest.write_text("\n".join(md_lines), encoding="utf-8")

        print("\n" + "=" * 80)
        print(f"✅ BATES STAMPING COMPLETE: {len(manifest_exhibits)} Exhibits Stamped")
        print(f"  JSON Manifest : {json_manifest}")
        print(f"  MD Index      : {md_manifest}")
        print("=" * 80)

        return manifest_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="APEX Forensic Bates Stamper")
    parser.add_argument("input_dir", help="Directory containing documents to stamp")
    parser.add_argument("--output-dir", "-o", default="./stamped_evidence", help="Output directory")
    parser.add_argument("--prefix", "-p", default="CYBER-", help="Bates prefix")
    parser.add_argument("--start", "-s", type=int, default=1001, help="Starting Bates number")
    args = parser.parse_args()

    ApexBatesStamper.stamp_collection(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir),
        prefix=args.prefix,
        start_number=args.start,
    )
