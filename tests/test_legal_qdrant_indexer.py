#!/usr/bin/env python3
"""
UNIT TESTS FOR APEX LEGAL QDRANT CLOUD INDEXER
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add legal tech directory
sys.path.insert(0, "/Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE/LEGAL_TECH")
from apex_legal_qdrant_indexer import (
    ApexLegalMasterIndexer,
    ApexLegalQdrantClient,
    LegalHardwareVectorizer,
)


def test_legal_hardware_vectorizer():
    text = "Hawaii Family Court Rule 60(b)(4) Void Ab Initio Extrinsic Fraud"
    vec = LegalHardwareVectorizer.vectorize(text, dim=1024)
    assert len(vec) == 1024
    assert any(x > 0.0 for x in vec)


def test_deterministic_point_id_generation():
    pid1 = ApexLegalMasterIndexer.generate_point_id("evidence_item_001")
    pid2 = ApexLegalMasterIndexer.generate_point_id("evidence_item_001")
    pid3 = ApexLegalMasterIndexer.generate_point_id("evidence_item_002")
    assert pid1 == pid2
    assert pid1 != pid3
    assert isinstance(pid1, int)


def test_qdrant_collections_query():
    colls = ApexLegalQdrantClient.get_collections()
    assert isinstance(colls, list)
    expected = ["actors", "case_documents", "case_law", "claims_evidence", "evidence_items", "timeline_events"]
    for exp in expected:
        assert exp in colls


def test_qdrant_semantic_search():
    hits = ApexLegalMasterIndexer.query_case_vault("39 seconds impossible decree", limit=3)
    assert isinstance(hits, list)
    assert len(hits) > 0
    first_hit = hits[0]
    assert "collection" in first_hit
    assert "score" in first_hit
    assert "payload" in first_hit
