#!/usr/bin/env python3
"""
APEX MASTER ESTATE CATALOGER (v1.0)
Standard: L2 Epistemic Inventory & Structural Topology
Features:
  - Deep-scans all repositories across DOMAINS, ENGINES, INFRASTRUCTURE, and ARCHIVE.
  - Extracts git remotes, languages, commit counts, and documentation manifests.
  - Generates comprehensive ESTATE_CATALOG.md and structured ESTATE_TOPOLOGY.json.
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

ESTATE_ROOT = Path("/Users/kcbflux/APEX_SYSTEM").resolve()
OUTPUT_MD = ESTATE_ROOT / "INFRASTRUCTURE" / "apex-core" / "docs" / "ESTATE_CATALOG.md"
OUTPUT_JSON = ESTATE_ROOT / "INFRASTRUCTURE" / "apex-core" / "docs" / "ESTATE_TOPOLOGY.json"


def get_git_info(repo_dir: Path) -> Dict[str, Any]:
    """Extract git origin, branch, and recent commit metadata."""
    info = {"is_git": False, "remotes": [], "branch": "", "commit_count": 0, "last_commit": ""}
    git_dir = repo_dir / ".git"
    if not git_dir.exists():
        return info

    info["is_git"] = True
    try:
        # Get remotes
        res = subprocess.run(
            ["git", "-C", str(repo_dir), "remote", "-v"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            lines = res.stdout.strip().split("\n")
            remotes = set()
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    remotes.add(f"{parts[0]}: {parts[1]}")
            info["remotes"] = list(remotes)

        # Get current branch
        res_b = subprocess.run(
            ["git", "-C", str(repo_dir), "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res_b.returncode == 0:
            info["branch"] = res_b.stdout.strip()

        # Get commit count
        res_c = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res_c.returncode == 0:
            info["commit_count"] = int(res_c.stdout.strip())

        # Get last commit message & date
        res_l = subprocess.run(
            ["git", "-C", str(repo_dir), "log", "-1", "--format=%cd (%cr) - %s"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res_l.returncode == 0:
            info["last_commit"] = res_l.stdout.strip()

    except Exception:
        pass

    return info


def detect_languages_and_files(repo_dir: Path) -> Dict[str, Any]:
    """Scan extensions and file counts."""
    ext_counts: Dict[str, int] = {}
    total_files = 0
    total_size = 0
    has_readme = False
    readme_snippet = ""

    for item in repo_dir.rglob("*"):
        if any(part in item.parts for part in (".git", "node_modules", "__pycache__", ".venv", "dist", "build")):
            continue
        if item.is_file():
            total_files += 1
            try:
                total_size += item.stat().st_size
            except Exception:
                pass
            ext = item.suffix.lower() or "no_ext"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

            if item.name.lower() in ("readme.md", "readme.txt", "readme"):
                has_readme = True
                try:
                    lines = item.read_text(encoding="utf-8", errors="ignore").split("\n")
                    non_empty = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
                    if non_empty:
                        readme_snippet = " ".join(non_empty[:2])[:180]
                except Exception:
                    pass

    return {
        "total_files": total_files,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "extensions": sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        "has_readme": has_readme,
        "readme_snippet": readme_snippet,
    }


def scan_estate() -> Dict[str, Any]:
    """Traverse and catalog all domains, engines, and infrastructure."""
    catalog: Dict[str, List[Dict[str, Any]]] = {
        "PORTFOLIO_ESTATE": [],
        "LEGAL_WARFARE": [],
        "SWARM_INTELLIGENCE": [],
        "AEROSPACE_MECHANICS": [],
        "IDENTITY_AND_PORTFOLIO": [],
        "ENGINES": [],
        "INFRASTRUCTURE": [],
        "ARCHIVE_CODEX": [],
    }

    # 1. PORTFOLIO_ESTATE
    pe_dir = ESTATE_ROOT / "DOMAINS" / "PORTFOLIO_ESTATE"
    if pe_dir.exists():
        for item in sorted(pe_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                git_info = get_git_info(item)
                file_info = detect_languages_and_files(item)
                catalog["PORTFOLIO_ESTATE"].append({
                    "name": item.name,
                    "path": str(item),
                    "git": git_info,
                    "metrics": file_info,
                })

    # 2. LEGAL_WARFARE
    lw_dir = ESTATE_ROOT / "DOMAINS" / "LEGAL_WARFARE"
    if lw_dir.exists():
        for item in sorted(lw_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                git_info = get_git_info(item)
                file_info = detect_languages_and_files(item)
                catalog["LEGAL_WARFARE"].append({
                    "name": item.name,
                    "path": str(item),
                    "git": git_info,
                    "metrics": file_info,
                })

    # 3. SWARM_INTELLIGENCE
    sw_dir = ESTATE_ROOT / "DOMAINS" / "SWARM_INTELLIGENCE"
    if sw_dir.exists():
        for item in sorted(sw_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                git_info = get_git_info(item)
                file_info = detect_languages_and_files(item)
                catalog["SWARM_INTELLIGENCE"].append({
                    "name": item.name,
                    "path": str(item),
                    "git": git_info,
                    "metrics": file_info,
                })

    # 4. ENGINES
    eng_dir = ESTATE_ROOT / "ENGINES"
    if eng_dir.exists():
        for item in sorted(eng_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                git_info = get_git_info(item)
                file_info = detect_languages_and_files(item)
                catalog["ENGINES"].append({
                    "name": item.name,
                    "path": str(item),
                    "git": git_info,
                    "metrics": file_info,
                })

    # 5. INFRASTRUCTURE
    inf_dir = ESTATE_ROOT / "INFRASTRUCTURE"
    if inf_dir.exists():
        for item in sorted(inf_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                git_info = get_git_info(item)
                file_info = detect_languages_and_files(item)
                catalog["INFRASTRUCTURE"].append({
                    "name": item.name,
                    "path": str(item),
                    "git": git_info,
                    "metrics": file_info,
                })

    # 6. ARCHIVE Codex
    cdx_dir = ESTATE_ROOT / "ARCHIVE" / "Codex"
    if cdx_dir.exists():
        for item in sorted(cdx_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                file_info = detect_languages_and_files(item)
                catalog["ARCHIVE_CODEX"].append({
                    "name": item.name,
                    "path": str(item),
                    "metrics": file_info,
                })

    return catalog


def generate_markdown(catalog: Dict[str, Any]) -> str:
    """Render catalog into a beautiful Markdown report."""
    total_repos = sum(len(v) for v in catalog.values())
    total_files = sum(sum(r["metrics"]["total_files"] for r in v) for v in catalog.values())
    total_size = sum(sum(r["metrics"]["total_size_mb"] for r in v) for v in catalog.values())

    md = [
        "# 🏛️ APEX MASTER ESTATE CATALOG & STRUCTURAL TOPOGRAPHY",
        "",
        f"> **Generated at:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"> **Total Cataloged Units:** {total_repos} repositories & functional vaults  ",
        f"> **Total Managed Files:** {total_files:,} files | **Total Volume:** {total_size / 1024:.2f} GB  ",
        "",
        "---",
        "",
    ]

    for section, items in catalog.items():
        md.append(f"## 📁 {section.replace('_', ' ')} ({len(items)} Units)")
        md.append("")
        if not items:
            md.append("*No active sub-repositories registered.*")
            md.append("")
            continue

        md.append("| Repository / Vault | Files | Size (MB) | Primary Types | Git Remote / Origin | Description / Snippet |")
        md.append("|:---|---:|---:|:---|:---|:---|")

        for r in items:
            name = r["name"]
            metrics = r["metrics"]
            git = r.get("git", {})
            remotes = "<br/>".join(git.get("remotes", [])) if git.get("remotes") else "*Local Only*"
            types = ", ".join(f"`{k}` ({v})" for k, v in metrics["extensions"][:3]) if metrics["extensions"] else "None"
            desc = metrics["readme_snippet"] or ("*Has README*" if metrics["has_readme"] else "*No README*")
            desc = desc.replace("|", "/")

            md.append(f"| **{name}** | {metrics['total_files']:,} | {metrics['total_size_mb']} | {types} | {remotes} | {desc} |")

        md.append("")
        md.append("---")
        md.append("")

    return "\n".join(md)


def main():
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)

    print("🔍 Deep-scanning APEX Master Estate...")
    catalog = scan_estate()

    OUTPUT_JSON.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"✅ Saved JSON Topology to: {OUTPUT_JSON}")

    md_content = generate_markdown(catalog)
    OUTPUT_MD.write_text(md_content, encoding="utf-8")
    print(f"✅ Generated Master Estate Catalog at: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
