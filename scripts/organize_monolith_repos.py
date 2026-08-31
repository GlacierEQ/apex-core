#!/usr/bin/env python3
"""
================================================================================
APEX MASTER MONOLITH REPOSITORY ORGANIZER & CARTOGRAPHY ENGINE
================================================================================
Permanent Location: /Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts/organize_monolith_repos.py
Standard: Holographic Mesh Taxonomy, Strict TECH vs DATA Ontological Separation,
          100% Disk-to-Catalog Parity, and Deterministic JSON/Markdown Synthesis.
================================================================================
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

APEX_ROOT = Path("/Users/kcbflux/APEX_SYSTEM").resolve()
APEX_CORE = APEX_ROOT / "INFRASTRUCTURE" / "apex-core"
TAXONOMY_JSON = APEX_CORE / "MONOLITH_ESTATE_TAXONOMY_MAP.json"
TAXONOMY_MD = APEX_CORE / "MONOLITH_ESTATE_TAXONOMY_MAP.md"
MESH_MAP_MD = APEX_CORE / "REPOSITORY_MESH_MAP.md"
DOCS_DIR = APEX_CORE / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
TOPOLOGY_JSON = DOCS_DIR / "ESTATE_TOPOLOGY.json"
CATALOG_MD = DOCS_DIR / "ESTATE_CATALOG.md"


def classify_repo(repo_name: str, repo_path: str, desc: str = "") -> Tuple[str, str]:
    """
    Classify any repository into its canonical Monolith Category and Subcategory.
    Enforces strict ontological separation between Technology (Engines & Tools) and Data (Evidence & State).
    """
    n = repo_name.lower()
    p = repo_path.lower()
    d = (desc or "").lower()

    # 0. ARCHIVE
    if "archive" in p or "legacy" in n or "backup" in n or "uninstalled" in n or "omnibus" in n:
        return ("ARCHIVE", "ARCHIVE_DATA")

    # 1. LEGAL & FORENSICS
    if (
        any(k in n for k in ["1fdv", "case-", "cybertack", "docket", "evidence", "legal", "pleading", "bates", "forensic", "court", "juriscraper", "eyecite"])
        or "legal_warfare" in p
        or "legal_data" in p
        or "legal_tech" in p
    ):
        if any(k in n for k in ["data", "evidence", "docket", "1fdv", "photo", "document", "codex"]) and not any(
            k in n for k in ["builder", "engine", "indexer", "stamper", "server", "mcp", "parser", "scraper"]
        ):
            return ("LEGAL", "LEGAL_DATA")
        return ("LEGAL", "LEGAL_TECH")

    # 2. AEROSPACE & SPACEX
    if any(k in n for k in ["spacex", "orbital", "propulsion", "launch", "cryogenics", "conjunction", "telemetry", "aerospace"]) or "aerospace_mechanics" in p:
        if "data" in n or "telemetry-lake" in n:
            return ("AEROSPACE", "AEROSPACE_DATA")
        return ("AEROSPACE", "AEROSPACE_TECH")

    # 3. SWARM & AGENTS
    if (
        any(k in n for k in ["swarm", "akos", "aspen", "mastermind", "babel", "tower", "dialectic", "agent", "openclaw", "tasklet", "manus", "comet"])
        or "swarm_intelligence" in p
    ):
        if "data" in n or "logs" in n or "transcripts" in n:
            return ("SWARM", "SWARM_DATA")
        return ("SWARM", "SWARM_TECH")

    # 4. AI_ML & ACCELERATED COMPUTE
    if (
        any(k in n for k in ["colossus", "reasoning", "quantizer", "trainium", "deepseek", "llama", "moe", "grok", "mooncake", "openai", "tpu", "metal", "vector", "omni_engine"])
        or "ml_intelligence" in p
        or "engines" in p
    ):
        if "data" in n or "index-lake" in n:
            return ("AI_ML", "AI_ML_DATA")
        return ("AI_ML", "AI_ML_TECH")

    # 5. INFRASTRUCTURE & MCP SERVERS & RUNTIMES
    if (
        any(k in n for k in ["apex-core", "control-plane", "computer-user", "mcp", "gateway", "singularity", "job-app-helix", "skills", "genius", "rclone", "fs-commander"])
        or "infrastructure" in p
        or "runtimes" in p
    ):
        if "data" in n or "records" in n:
            return ("INFRASTRUCTURE", "INFRASTRUCTURE_DATA")
        return ("INFRASTRUCTURE", "INFRASTRUCTURE_TECH")

    # 6. DOC_GEN
    if any(k in n for k in ["doc-gen", "latex", "pdf", "brief", "typst", "whisper"]):
        return ("DOC_GEN", "DOC_GEN_TECH")

    # 7. Default to PORTFOLIO_TECH
    return ("PORTFOLIO", "PORTFOLIO_TECH")


def get_git_metadata(repo_dir: Path) -> Dict[str, Any]:
    """Extract git remotes, branch, commit count, and latest commit info."""
    meta = {
        "is_git": False,
        "remotes": [],
        "github_url": None,
        "branch": "main",
        "commit_count": 0,
        "last_commit": "",
        "is_fork": False,
        "is_private": True,
    }
    git_dir = repo_dir / ".git"
    if not git_dir.exists():
        return meta

    meta["is_git"] = True
    try:
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
                    remotes.add(parts[1])
                    if "github.com" in parts[1]:
                        url = parts[1]
                        if url.endswith(".git"):
                            url = url[:-4]
                        meta["github_url"] = url
            meta["remotes"] = sorted(list(remotes))

        res_b = subprocess.run(
            ["git", "-C", str(repo_dir), "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res_b.returncode == 0 and res_b.stdout.strip():
            meta["branch"] = res_b.stdout.strip()

        res_c = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res_c.returncode == 0 and res_c.stdout.strip().isdigit():
            meta["commit_count"] = int(res_c.stdout.strip())

        res_l = subprocess.run(
            ["git", "-C", str(repo_dir), "log", "-1", "--format=%cd (%cr) - %s"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res_l.returncode == 0:
            meta["last_commit"] = res_l.stdout.strip()

    except Exception:
        pass

    return meta


def get_repo_metrics(repo_dir: Path) -> Dict[str, Any]:
    """Scan file extensions, size, and documentation snippets."""
    ext_counts: Dict[str, int] = {}
    total_files = 0
    total_size = 0
    has_readme = False
    readme_snippet = ""
    has_agents_md = (repo_dir / "AGENTS.md").exists()
    has_helix_md = (repo_dir / "HELIX.md").exists()

    for item in repo_dir.rglob("*"):
        if any(p in item.parts for p in (".git", "node_modules", "__pycache__", ".venv", "dist", "build", ".pytest_cache")):
            continue
        if item.is_file():
            total_files += 1
            try:
                total_size += item.stat().st_size
            except Exception:
                pass
            ext = item.suffix.lower() or "no_ext"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

            if item.name.lower() in ("readme.md", "readme.txt", "readme") and not readme_snippet:
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
        "primary_extensions": sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        "has_readme": has_readme,
        "has_agents_md": has_agents_md,
        "has_helix_md": has_helix_md,
        "description": readme_snippet or "APEX Sovereign Repository",
    }


def find_all_local_git_repos() -> List[Path]:
    """Find all local git repository directories under APEX_SYSTEM and project paths."""
    cmd = [
        "find",
        str(APEX_ROOT),
        "-name",
        ".git",
        "-type",
        "d",
        "-not",
        "-path",
        "*/node_modules/*",
        "-not",
        "-path",
        "*/.venv/*",
        "-not",
        "-path",
        "*/.cache/*",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    repos = [Path(line).parent.resolve() for line in res.stdout.strip().split("\n") if line]
    return sorted(list(set(repos)))


def organize_monolith_catalog() -> Dict[str, Any]:
    """
    Main orchestration routine:
    1. Reads existing MONOLITH_ESTATE_TAXONOMY_MAP.json
    2. Scans all physical git repositories on disk
    3. Merges and updates all entries
    4. Writes updated JSON, Markdown, and Topology files
    """
    print("=== APEX MASTER MONOLITH REPOSITORY ORGANIZER ===", flush=True)

    # 1. Load existing map
    existing_catalog: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    if TAXONOMY_JSON.exists():
        with open(TAXONOMY_JSON) as f:
            existing_catalog = json.load(f)

    # Flatten existing repo index by name and github_url
    existing_by_name: Dict[str, Dict[str, Any]] = {}
    for cat, subcats in existing_catalog.items():
        for subcat, repos in subcats.items():
            for r in repos:
                existing_by_name[r["name"].lower()] = r

    # 2. Discover all local physical repositories
    local_repos = find_all_local_git_repos()
    print(f"Discovered {len(local_repos)} physical git repositories on disk.")

    # 3. Process every local repo
    processed_local_names: Set[str] = set()
    updated_local_entries: List[Dict[str, Any]] = []

    for repo_path in local_repos:
        name = repo_path.name
        git_meta = get_git_metadata(repo_path)
        metrics = get_repo_metrics(repo_path)
        
        # Check if repo was already in catalog
        prior = existing_by_name.get(name.lower(), {})
        desc = prior.get("description") or metrics["description"]
        cat = prior.get("category")
        subcat = prior.get("subcategory")

        if not cat or not subcat:
            cat, subcat = classify_repo(name, str(repo_path), desc)

        entry = {
            "name": name,
            "description": desc,
            "category": cat,
            "subcategory": subcat,
            "is_private": prior.get("is_private", True),
            "is_local_cloned": True,
            "local_path": str(repo_path),
            "github_url": git_meta["github_url"] or prior.get("github_url") or f"https://github.com/GlacierEQ/{name}",
            "is_fork": prior.get("is_fork", False),
            "branch": git_meta["branch"],
            "commit_count": git_meta["commit_count"],
            "last_commit": git_meta["last_commit"],
            "total_files": metrics["total_files"],
            "total_size_mb": metrics["total_size_mb"],
            "has_agents_md": metrics["has_agents_md"],
            "has_helix_md": metrics["has_helix_md"],
        }
        updated_local_entries.append(entry)
        processed_local_names.add(name.lower())

    # 4. Build consolidated Monolith Taxonomy
    master_taxonomy: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
        "LEGAL": {"LEGAL_TECH": [], "LEGAL_DATA": []},
        "DOC_GEN": {"DOC_GEN_TECH": [], "DOC_GEN_DATA": []},
        "SWARM": {"SWARM_TECH": [], "SWARM_DATA": []},
        "AI_ML": {"AI_ML_TECH": [], "AI_ML_DATA": []},
        "AEROSPACE": {"AEROSPACE_TECH": [], "AEROSPACE_DATA": []},
        "INFRASTRUCTURE": {"INFRASTRUCTURE_TECH": [], "INFRASTRUCTURE_DATA": []},
        "PORTFOLIO": {"PORTFOLIO_TECH": [], "PORTFOLIO_DATA": []},
        "ARCHIVE": {"ARCHIVE_DATA": []},
    }

    # Add all local entries
    for entry in updated_local_entries:
        cat = entry["category"]
        subcat = entry["subcategory"]
        if cat not in master_taxonomy:
            master_taxonomy[cat] = {}
        if subcat not in master_taxonomy[cat]:
            master_taxonomy[cat][subcat] = []
        master_taxonomy[cat][subcat].append(entry)

    # Retain all remote-only entries from existing catalog
    remote_count = 0
    for cat, subcats in existing_catalog.items():
        for subcat, repos in subcats.items():
            for r in repos:
                name_l = r["name"].lower()
                if name_l not in processed_local_names:
                    # Remote-only entry
                    r["is_local_cloned"] = False
                    r["local_path"] = None
                    if cat not in master_taxonomy:
                        master_taxonomy[cat] = {}
                    if subcat not in master_taxonomy[cat]:
                        master_taxonomy[cat][subcat] = []
                    master_taxonomy[cat][subcat].append(r)
                    remote_count += 1

    # Sort all subcategory arrays by name
    for cat in master_taxonomy:
        for subcat in master_taxonomy[cat]:
            master_taxonomy[cat][subcat].sort(key=lambda x: (not x.get("is_local_cloned", False), x["name"].lower()))

    # 5. Write updated JSON map
    with open(TAXONOMY_JSON, "w") as f:
        json.dump(master_taxonomy, f, indent=2)
    print(f"Wrote updated Monolith JSON map -> {TAXONOMY_JSON}")

    # 6. Generate updated Markdown map
    md_content = generate_markdown_map(master_taxonomy, len(updated_local_entries), remote_count)
    with open(TAXONOMY_MD, "w") as f:
        f.write(md_content)
    print(f"Wrote updated Monolith Markdown map -> {TAXONOMY_MD}")

    # 7. Generate Estate Topology
    topology_data = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_repositories": len(updated_local_entries) + remote_count,
        "local_cloned_count": len(updated_local_entries),
        "remote_only_count": remote_count,
        "categories": {
            cat: {
                subcat: len(repos)
                for subcat, repos in subcats.items()
            }
            for cat, subcats in master_taxonomy.items()
        },
        "local_repositories": [
            {
                "name": e["name"],
                "path": e["local_path"],
                "category": e["category"],
                "subcategory": e["subcategory"],
                "branch": e.get("branch"),
                "commit_count": e.get("commit_count"),
                "total_files": e.get("total_files"),
                "total_size_mb": e.get("total_size_mb"),
            }
            for e in updated_local_entries
        ],
    }
    with open(TOPOLOGY_JSON, "w") as f:
        json.dump(topology_data, f, indent=2)
    print(f"Wrote Estate Topology JSON -> {TOPOLOGY_JSON}")

    print(f"=== MONOLITH CARTOGRAPHY COMPLETE: {len(updated_local_entries)} Local, {remote_count} Remote ===")
    return master_taxonomy


def generate_markdown_map(taxonomy: Dict[str, Dict[str, List[Dict[str, Any]]]], local_count: int, remote_count: int) -> str:
    """Generate master human-readable Markdown taxonomy document."""
    total_repos = local_count + remote_count
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# 🏛️ APEX Master Monolith Estate Taxonomy Map",
        "",
        f"> **Generated:** {now_str}  ",
        f"> **Total Repositories:** {total_repos} ({local_count} Local Cloned, {remote_count} Remote)  ",
        f"> **Standard:** Holographic Mesh Taxonomy & Strict Ontological Separation of Category (Domain) and Subcategory (TECH vs DATA).",
        "",
        "---",
        "",
        "## 📊 Summary by Category & Subcategory",
        "",
        "| Category | Subcategory (TECH) | Subcategory (DATA) | Total |",
        "|---|:---:|:---:|:---:|",
    ]

    for cat, subcats in taxonomy.items():
        tech_count = len(subcats.get(f"{cat}_TECH", []))
        data_count = len(subcats.get(f"{cat}_DATA", []))
        cat_total = sum(len(repos) for repos in subcats.values())
        lines.append(f"| **`{cat}`** | {tech_count} repos | {data_count} repos | **{cat_total} repos** |")

    lines.extend([
        f"| **TOTALS** | — | — | **{total_repos} repos** |",
        "",
        "---",
        "",
    ])

    # Category Detail Tables
    for cat, subcats in taxonomy.items():
        lines.append(f"## 📁 Category: `{cat}`")
        lines.append("")
        for subcat, repos in subcats.items():
            icon = "⚙️" if "TECH" in subcat else "📁"
            lines.append(f"### {icon} Subcategory: `{subcat}` ({len(repos)} Repositories)")
            lines.append("")
            lines.append("| Repository Name | Local Cloned | Location / Remote | Description |")
            lines.append("|---|:---:|---|---|")
            for r in repos:
                name = r["name"]
                url = r.get("github_url") or f"https://github.com/GlacierEQ/{name}"
                is_local = r.get("is_local_cloned", False)
                local_path = r.get("local_path")
                status_icon = "🟢 Yes" if is_local else "⚪ Remote"
                loc_str = f"[`{local_path}`](file://{local_path})" if is_local and local_path else f"[{name}]({url})"
                desc = r.get("description", "—").replace("|", "\\|")
                if len(desc) > 200:
                    desc = desc[:197] + "..."
                lines.append(f"| [`{name}`]({url}) | {status_icon} | {loc_str} | {desc} |")
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    organize_monolith_catalog()
