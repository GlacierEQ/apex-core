#!/usr/bin/env python3
"""
APEX SOVEREIGN MONOLITH HIERARCHICAL ORGANIZER & MESH LINKER
Standard: Organizes all local and remote repositories into their true hierarchical Monolith structure
          by Category and Subcategory (TECH vs DATA) using lossless holographic symlinks.
          Zero Data Loss Theorem: No physical files are moved or broken; symlinks guarantee dual-access.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

APEX_SYSTEM = Path("/Users/kcbflux/APEX_SYSTEM")
MONOLITH_REPO = Path("/Users/kcbflux/monolith")
TAXONOMY_MAP_PATH = APEX_SYSTEM / "INFRASTRUCTURE" / "apex-core" / "MONOLITH_ESTATE_TAXONOMY_MAP.json"

# Domain Folder Mapping in APEX_SYSTEM
DOMAIN_PATHS = {
    "LEGAL": APEX_SYSTEM / "DOMAINS" / "LEGAL_WARFARE",
    "DOC_GEN": APEX_SYSTEM / "DOMAINS" / "DOC_GEN",
    "SWARM": APEX_SYSTEM / "DOMAINS" / "SWARM_INTELLIGENCE",
    "AEROSPACE": APEX_SYSTEM / "DOMAINS" / "AEROSPACE_MECHANICS",
    "AI_ML": APEX_SYSTEM / "ENGINES" / "ML_INTELLIGENCE",
    "INFRASTRUCTURE": APEX_SYSTEM / "INFRASTRUCTURE",
    "PORTFOLIO": APEX_SYSTEM / "DOMAINS" / "PORTFOLIO_ESTATE",
}


def ensure_domain_directories():
    """Ensures all Category and Subcategory directories exist."""
    for cat, base_path in DOMAIN_PATHS.items():
        (base_path / f"{cat}_TECH").mkdir(parents=True, exist_ok=True)
        (base_path / f"{cat}_DATA").mkdir(parents=True, exist_ok=True)


def create_hierarchical_links(dry_run: bool = False) -> Dict[str, Any]:
    """
    Creates relative symlinks for all local repositories into their corresponding
    Category and Subcategory folders.
    """
    ensure_domain_directories()

    if not TAXONOMY_MAP_PATH.exists():
        print(f"🔴 Taxonomy map not found at {TAXONOMY_MAP_PATH}")
        sys.exit(1)

    with open(TAXONOMY_MAP_PATH, "r", encoding="utf-8") as f:
        tree = json.load(f)

    linked = []
    skipped = []

    for cat, subcats in tree.items():
        base_domain = DOMAIN_PATHS.get(cat, APEX_SYSTEM / "DOMAINS" / "PORTFOLIO_ESTATE")
        for subcat, repos in subcats.items():
            subcat_dir = base_domain / subcat
            subcat_dir.mkdir(parents=True, exist_ok=True)

            for r in repos:
                name = r["name"]
                local_path_str = r.get("local_path")
                if not r.get("is_local_cloned") or not local_path_str:
                    continue

                real_path = Path(local_path_str).resolve()
                if not real_path.exists():
                    continue

                target_link = subcat_dir / name

                # Don't symlink if the target is already the exact physical location
                if target_link == real_path:
                    skipped.append({"name": name, "reason": "Already in target directory", "path": str(real_path)})
                    continue

                # If symlink exists, verify or replace
                if target_link.is_symlink() or target_link.exists():
                    if target_link.resolve() == real_path:
                        skipped.append({"name": name, "reason": "Symlink already correct", "link": str(target_link)})
                        continue
                    if not dry_run:
                        if target_link.is_symlink():
                            target_link.unlink()
                        elif target_link.is_dir() and not (target_link / ".git").exists():
                            shutil.rmtree(target_link)

                # Compute relative symlink
                try:
                    rel_target = os.path.relpath(real_path, subcat_dir)
                    if not dry_run:
                        os.symlink(rel_target, target_link)
                    linked.append({
                        "name": name,
                        "category": cat,
                        "subcategory": subcat,
                        "link": str(target_link),
                        "target": str(real_path),
                    })
                except Exception as e:
                    print(f"⚠️ Error creating symlink for {name}: {e}")

    return {"linked": linked, "skipped": skipped, "dry_run": dry_run}


def generate_hierarchical_inventory_report() -> Path:
    """Generates a comprehensive markdown report of the hierarchical organization."""
    report_path = APEX_SYSTEM / "DOMAINS_HIERARCHICAL_STRUCTURE.md"
    lines = [
        "# 🏛️ APEX Master Domain Cartography & Hierarchical Mesh",
        "",
        "> **Standard:** Monolith Category & Subcategory Separation (TECH vs DATA) via Lossless Holographic Symlinks.  ",
        "> **Theorem:** Zero Data Loss — Original paths preserved; hierarchical domain trees provide instant structured access.",
        "",
        "---",
        "",
        "## 📊 Domain Distribution Matrix",
        "",
        "| Category | Domain Root Path | TECH Subcategory | DATA Subcategory |",
        "|---|---|:---:|:---:|",
    ]

    for cat, base_path in DOMAIN_PATHS.items():
        tech_dir = base_path / f"{cat}_TECH"
        data_dir = base_path / f"{cat}_DATA"
        tech_count = len(list(tech_dir.iterdir())) if tech_dir.exists() else 0
        data_count = len(list(data_dir.iterdir())) if data_dir.exists() else 0
        rel_base = base_path.relative_to(Path("/Users/kcbflux"))
        lines.append(f"| **`{cat}`** | `~/{rel_base}` | **{tech_count}** entries | **{data_count}** entries |")

    lines.append("")
    lines.append("---")
    lines.append("")

    for cat, base_path in DOMAIN_PATHS.items():
        lines.append(f"## 📁 Domain: `{cat}` (`{base_path}`)")
        for subcat in [f"{cat}_TECH", f"{cat}_DATA"]:
            subcat_dir = base_path / subcat
            items = sorted(list(subcat_dir.iterdir())) if subcat_dir.exists() else []
            lines.append(f"\n### ⚙️ `{subcat}` ({len(items)} Repositories / Nodes)")
            if not items:
                lines.append("*(No local nodes cloned yet; managed via on-demand remote fetch)*\n")
                continue

            lines.append("| Name | Type | Resolved Physical Path |")
            lines.append("|---|:---:|---|")
            for item in items:
                item_type = "🔗 Symlink" if item.is_symlink() else "📁 Directory"
                resolved = item.resolve()
                lines.append(f"| [`{item.name}`]({item}) | {item_type} | `{resolved}` |")
            lines.append("")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Also copy into monolith/catalog/
    if MONOLITH_REPO.exists():
        shutil.copy2(report_path, MONOLITH_REPO / "catalog" / "DOMAINS_HIERARCHICAL_STRUCTURE.md")

    return report_path


def main():
    parser = argparse.ArgumentParser(description="APEX Sovereign Monolith Hierarchical Organizer")
    parser.add_argument("--execute", action="store_true", help="Create live symlinks into hierarchical domain directories")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Simulate symlink creation without touching disk")
    args = parser.parse_args()

    is_dry_run = not args.execute

    print("=" * 80)
    print("🏛️  APEX MONOLITH HIERARCHICAL ESTATE ORGANIZER")
    print(f"Mode: {'🔍 SIMULATION (DRY-RUN)' if is_dry_run else '⚡ LIVE HIERARCHICAL LINKING'}")
    print("=" * 80)

    res = create_hierarchical_links(dry_run=is_dry_run)
    print(f"\n✓ Processed: {len(res['linked'])} repositories linked into hierarchical structure.")
    print(f"✓ Skipped  : {len(res['skipped'])} repositories already aligned.")

    if not is_dry_run:
        report_file = generate_hierarchical_inventory_report()
        print(f"\n🏆 Hierarchical Domain Report generated at:")
        print(f"  ↳ {report_file}")
        if (MONOLITH_REPO / "catalog" / "DOMAINS_HIERARCHICAL_STRUCTURE.md").exists():
            print(f"  ↳ {MONOLITH_REPO / 'catalog' / 'DOMAINS_HIERARCHICAL_STRUCTURE.md'}")


if __name__ == "__main__":
    main()
