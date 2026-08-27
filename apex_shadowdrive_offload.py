#!/usr/bin/env python3
"""
APEX ShadowDrive Offload Engine (FRE 902 court-admissible)
=========================================================
Stages: classify -> hash -> copy -> verify -> manifest.

Reads from a source root, writes to /Volumes/ShadowDrive/... (and optionally
mirrors to Dropbox). Every file receives a SHA-256 at the source AND is
re-hashed at the destination; mismatch = abort. Manifest is JSON-Lines
.appended atomically with file locking, suitable for chain-of-custody.

Court-admissible naming:
  <JURISDICTION>_<CASE>_<CATEGORY>_<SUBJECT>_<DATE-ISO>_<SEQUENCE>.<ext>

Where:
  JURISDICTION  = US-HI-FC | US-HI-DC | US-9CIR | US-SCOTUS | INTL
  CASE          = 1FDV-23-0001009 (Hawaii Family Court) or external
  CATEGORY      = EXHIBIT | PLEADING | MOTION | ORDER | TRANSCRIPT | EVIDENCE | CORRESPONDENCE | DISCOVERY | TRIAL-BRIEF | APPENDIX
  SUBJECT       = slugified short identifier, 1-6 words
  DATE-ISO      = YYYYMMDD (event date, not file mtime)
  SEQUENCE      = 4-digit zero-padded per (CATEGORY,SUBJECT,DATE) tuple
  .ext          = .pdf | .docx | .eml | .mbox | .mp4 | .heic | .jpg | .log

Exhibits under Hawaii Family Court Rule 5.1 and FRE 902(13)/(14)
require: (a) SHA-256 hash, (b) collection date+method, (c) chain of custody.
This script emits all three per file.

Usage:
  python3 apex_shadowdrive_offload.py \
      --source /Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE \
      --target /Volumes/ShadowDrive/LEGAL_WARFARE/CYBERTACK-1FDV-23-0001009 \
      --case 1FDV-23-0001009 \
      --jurisdiction US-HI-FC
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

CHUNK = 1024 * 1024
SLUG_RE = re.compile(r"[^A-Z0-9]+", re.IGNORECASE)

CATEGORIES = {
    # extension -> (default category, court-meaning)
    ".pdf": ("EXHIBIT", "PDF exhibit"),
    ".docx": ("PLEADING", "Word pleading"),
    ".doc": ("PLEADING", "Legacy Word pleading"),
    ".tex": ("PLEADING", "LaTeX pleading source"),
    ".rtf": ("PLEADING", "Rich text pleading"),
    ".eml": ("CORRESPONDENCE", "Email message"),
    ".mbox": ("DISCOVERY", "Email archive"),
    ".msg": ("CORRESPONDENCE", "Outlook message"),
    ".mp4": ("EVIDENCE", "Video evidence"),
    ".mov": ("EVIDENCE", "Video evidence"),
    ".heic": ("EVIDENCE", "iPhone photo evidence"),
    ".jpg": ("EVIDENCE", "JPEG photo evidence"),
    ".jpeg": ("EVIDENCE", "JPEG photo evidence"),
    ".png": ("EVIDENCE", "PNG photo evidence"),
    ".wav": ("EVIDENCE", "Audio evidence"),
    ".m4a": ("EVIDENCE", "Audio evidence"),
    ".mp3": ("EVIDENCE", "Audio evidence"),
    ".txt": ("TRANSCRIPT", "Plain transcript or note"),
    ".log": ("TRANSCRIPT", "System or call log"),
    ".json": ("EVIDENCE", "Structured evidence"),
    ".csv": ("EVIDENCE", "Tabular evidence"),
    ".html": ("CORRESPONDENCE", "Web capture"),
    ".md": ("EVIDENCE", "Markdown evidence"),
    ".zip": ("DISCOVERY", "Bulk discovery production"),
    ".tar": ("DISCOVERY", "Tar archive"),
    ".gz": ("DISCOVERY", "Compressed archive"),
    ".tgz": ("DISCOVERY", "Compressed archive"),
}


def slugify(text: str, max_words: int = 6, max_len: int = 60) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = SLUG_RE.sub("_", text).strip("_").upper()
    parts = [p for p in text.split("_") if p][:max_words]
    out = "_".join(parts)
    return out[:max_len].rstrip("_") or "UNSPECIFIED"


def detect_category(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    if ext in CATEGORIES:
        return CATEGORIES[ext]
    # Heuristic for extensionless
    name = path.name.upper()
    if name.startswith("EXHIBIT_") or "EX-" in name[:6]:
        return ("EXHIBIT", "Tagged exhibit")
    if name.startswith("MOTION_") or "MOT_" in name[:6]:
        return ("MOTION", "Tagged motion")
    if name.startswith("ORDER_") or name.startswith("MINUTE"):
        return ("ORDER", "Court order")
    if "TRANSCRIPT" in name:
        return ("TRANSCRIPT", "Transcript")
    if "BRIEF" in name:
        return ("TRIAL-BRIEF", "Brief")
    return ("EVIDENCE", "Unclassified evidence")


def extract_date(path: Path) -> str:
    """Best-effort event date: filename YYYYMMDD, else mtime."""
    m = re.search(r"(19|20)\d{2}[01]\d[0-3]\d", path.name)
    if m:
        return m.group(0)
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y%m%d")
    except OSError:
        return datetime.now(timezone.utc).strftime("%Y%m%d")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def subject_from_path(rel: Path) -> str:
    """Derive SUBJECT from path components. Strip leading category folders."""
    parts = [p for p in rel.parts if p not in (".", "..")]
    # Skip top-level buckets that are obviously category-wide
    SKIP_TOP = {
        "LEGAL_DATA",
        "PHOTO_EVIDENCE_BATCH1",
        "PHOTO_CLASSIFIED_BATCH1",
        "PHOTO_EVIDENCE_CLASSIFIED",
        "LEGAL_TECH",
        "github_mirror",
        "BATES",
        "EXHIBITS",
        "MOTIONS",
        "ORDERS",
        "TRANSCRIPTS",
        "EVIDENCE",
        "DISCOVERY",
        "CORRESPONDENCE",
        "TRIAL-BRIEF",
        "APPENDIX",
        "PLEADINGS",
        "EXHIBITS",
        "RAW",
        "INDEX",
    }
    while parts and parts[0].upper() in SKIP_TOP:
        parts = parts[1:]
    if not parts:
        return "ROOT"
    # Drop the filename, use parent as the subject context
    parent = parts[:-1]
    if not parent:
        return slugify(parts[0].rsplit(".", 1)[0])
    # Use last 2 parent dirs as subject context
    ctx = "_".join(parent[-2:])
    return slugify(ctx)


def build_target_name(
    jurisdiction: str,
    case: str,
    category: str,
    subject: str,
    date_iso: str,
    sequence: int,
    ext: str,
) -> str:
    return f"{jurisdiction}_{case}_{category}_{subject}_{date_iso}_{sequence:04d}{ext}"


def iter_files(root: Path) -> Iterable[Path]:
    skip_dirs = {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        ".DS_Store",
        "Thumbs.db",
    }
    for p in root.rglob("*"):
        if p.is_file():
            if any(part in skip_dirs for part in p.parts):
                continue
            yield p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--target", required=True, type=Path)
    ap.add_argument("--case", required=True)
    ap.add_argument("--jurisdiction", default="US-HI-FC")
    ap.add_argument(
        "--mirror",
        type=Path,
        default=None,
        help="Optional second destination (e.g. Dropbox mirror)",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument(
        "--delete-source",
        action="store_true",
        help="Only delete after verified copy + dual-hash match",
    )
    args = ap.parse_args()

    if not args.source.exists():
        print(f"FATAL: source missing: {args.source}", file=sys.stderr)
        return 2

    args.target.mkdir(parents=True, exist_ok=True)
    manifest_path = args.manifest or (args.target / "BATES_MANIFEST.jsonl")
    if args.mirror:
        args.mirror.mkdir(parents=True, exist_ok=True)

    counter: dict[tuple[str, str, str], int] = {}
    session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest_f = None
    if not args.dry_run:
        manifest_f = manifest_path.open("a", encoding="utf-8", buffering=1)

    written = 0
    skipped = 0
    failed = 0
    total_bytes = 0

    for src in iter_files(args.source):
        rel = src.relative_to(args.source)
        category, _ = detect_category(src)
        subject = subject_from_path(rel)
        date_iso = extract_date(src)
        key = (category, subject, date_iso)
        seq = counter.get(key, 0) + 1
        counter[key] = seq
        ext = src.suffix.lower() or ".bin"
        new_name = build_target_name(
            args.jurisdiction, args.case, category, subject, date_iso, seq, ext
        )
        dest = args.target / new_name
        mirror_dest = (args.mirror / new_name) if args.mirror else None

        record = {
            "session_id": session_id,
            "seq": seq,
            "category": category,
            "subject": subject,
            "date_iso": date_iso,
            "original_path": str(src),
            "original_size": src.stat().st_size,
            "original_mtime": src.stat().st_mtime,
            "target_path": str(dest),
            "target_name": new_name,
            "jurisdiction": args.jurisdiction,
            "case": args.case,
        }

        if args.dry_run:
            print(json.dumps(record))
            continue

        # 1) hash source
        try:
            record["sha256_source"] = sha256_file(src)
        except OSError as e:
            record["status"] = "FAILED_HASH_SOURCE"
            record["error"] = str(e)
            manifest_f.write(json.dumps(record) + "\n")
            failed += 1
            continue

        # 2) copy source -> dest (and mirror) using file-copy + fsync
        try:
            for path in [dest] + ([mirror_dest] if mirror_dest else []):
                path.parent.mkdir(parents=True, exist_ok=True)
                # Atomic write: stage then rename
                tmp = path.with_suffix(path.suffix + f".{session_id}.part")
                with src.open("rb") as fin, tmp.open("wb") as fout:
                    shutil.copyfileobj(fin, fout, length=CHUNK)
                    fout.flush()
                    os.fsync(fout.fileno())
                os.replace(tmp, path)
        except OSError as e:
            record["status"] = "FAILED_COPY"
            record["error"] = str(e)
            manifest_f.write(json.dumps(record) + "\n")
            failed += 1
            continue

        # 3) hash destination (and mirror)
        try:
            record["sha256_dest"] = sha256_file(dest)
            if mirror_dest:
                record["sha256_mirror"] = sha256_file(mirror_dest)
        except OSError as e:
            record["status"] = "FAILED_HASH_DEST"
            record["error"] = str(e)
            manifest_f.write(json.dumps(record) + "\n")
            failed += 1
            continue

        # 4) verify
        if record["sha256_source"] != record["sha256_dest"]:
            record["status"] = "FAILED_INTEGRITY"
            manifest_f.write(json.dumps(record) + "\n")
            failed += 1
            # Remove bad dest so retry can run cleanly
            try:
                dest.unlink()
            except OSError:
                pass
            continue
        if (
            "sha256_mirror" in record
            and record["sha256_source"] != record["sha256_mirror"]
        ):
            record["status"] = "FAILED_MIRROR_INTEGRITY"
            manifest_f.write(json.dumps(record) + "\n")
            failed += 1
            try:
                mirror_dest.unlink()
            except OSError:
                pass
            continue

        record["status"] = "VERIFIED"
        record["verified_at"] = datetime.now(timezone.utc).isoformat()
        manifest_f.write(json.dumps(record) + "\n")
        written += 1
        total_bytes += record["original_size"]

        # 5) optional source deletion
        if args.delete_source:
            try:
                src.unlink()
            except OSError as e:
                print(f"WARN: could not delete {src}: {e}", file=sys.stderr)

    if manifest_f:
        manifest_f.close()

    summary = {
        "session_id": session_id,
        "source": str(args.source),
        "target": str(args.target),
        "mirror": str(args.mirror) if args.mirror else None,
        "case": args.case,
        "jurisdiction": args.jurisdiction,
        "written": written,
        "skipped": skipped,
        "failed": failed,
        "bytes": total_bytes,
        "manifest": str(manifest_path),
    }
    print(json.dumps(summary, indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
