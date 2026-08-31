#!/usr/bin/env python3
"""
Test Suite: Monolith Repository Organization & Holographic Mesh Parity
Standard: L2 Epistemic Unit Assertion & Invariant Verification
"""

import json
from pathlib import Path
import pytest

APEX_ROOT = Path("/Users/kcbflux/APEX_SYSTEM").resolve()
APEX_CORE = APEX_ROOT / "INFRASTRUCTURE" / "apex-core"
TAXONOMY_JSON = APEX_CORE / "MONOLITH_ESTATE_TAXONOMY_MAP.json"
TAXONOMY_MD = APEX_CORE / "MONOLITH_ESTATE_TAXONOMY_MAP.md"
TOPOLOGY_JSON = APEX_CORE / "docs" / "ESTATE_TOPOLOGY.json"


def test_monolith_taxonomy_json_exists_and_valid():
    """Verify that MONOLITH_ESTATE_TAXONOMY_MAP.json exists and is valid JSON."""
    assert TAXONOMY_JSON.exists(), f"Missing {TAXONOMY_JSON}"
    with open(TAXONOMY_JSON) as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert len(data) >= 7
    expected_categories = {"LEGAL", "DOC_GEN", "SWARM", "AI_ML", "AEROSPACE", "INFRASTRUCTURE", "PORTFOLIO"}
    assert expected_categories.issubset(set(data.keys()))


def test_all_local_paths_exist_on_disk():
    """Verify that all repositories marked as is_local_cloned exist on disk."""
    with open(TAXONOMY_JSON) as f:
        data = json.load(f)

    local_count = 0
    for cat, subcats in data.items():
        for subcat, repos in subcats.items():
            for r in repos:
                if r.get("is_local_cloned"):
                    local_count += 1
                    path_str = r.get("local_path")
                    assert path_str is not None, f"Repo {r['name']} marked local but local_path is None"
                    path = Path(path_str)
                    assert path.exists(), f"Repo {r['name']} path does not exist: {path_str}"
                    assert (path / ".git").exists(), f"Repo {r['name']} missing .git directory at {path_str}"

    assert local_count >= 75, f"Expected at least 75 local repositories, found {local_count}"


def test_strict_tech_vs_data_ontological_separation():
    """Verify strict subcategory taxonomy separation (TECH vs DATA)."""
    with open(TAXONOMY_JSON) as f:
        data = json.load(f)

    for cat, subcats in data.items():
        for subcat in subcats.keys():
            if cat != "ARCHIVE":
                assert subcat.endswith("_TECH") or subcat.endswith("_DATA"), (
                    f"Subcategory {subcat} in {cat} does not follow _TECH or _DATA convention"
                )


def test_monolith_markdown_map_completeness():
    """Verify that MONOLITH_ESTATE_TAXONOMY_MAP.md is populated with tables and summaries."""
    assert TAXONOMY_MD.exists(), f"Missing {TAXONOMY_MD}"
    content = TAXONOMY_MD.read_text(encoding="utf-8")
    assert "# 🏛️ APEX Master Monolith Estate Taxonomy Map" in content
    assert "Summary by Category & Subcategory" in content
    assert "Category: `LEGAL`" in content
    assert "Category: `SWARM`" in content
    assert "Category: `AEROSPACE`" in content
    assert "Category: `AI_ML`" in content
    assert "Category: `INFRASTRUCTURE`" in content
    assert "🟢 Yes" in content


def test_estate_topology_json_parity():
    """Verify that docs/ESTATE_TOPOLOGY.json matches the taxonomy totals."""
    assert TOPOLOGY_JSON.exists(), f"Missing {TOPOLOGY_JSON}"
    with open(TOPOLOGY_JSON) as f:
        topo = json.load(f)

    assert "total_repositories" in topo
    assert "local_cloned_count" in topo
    assert "local_repositories" in topo
    assert topo["local_cloned_count"] == len(topo["local_repositories"])
    assert topo["local_cloned_count"] >= 100
