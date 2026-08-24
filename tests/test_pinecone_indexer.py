#!/usr/bin/env python3
"""
UNIT TESTS FOR APEX PINECONE CLOUD INDEXER
"""

import sys
from pathlib import Path

# Add legal tech directory
sys.path.insert(0, "/Users/kcbflux/APEX_SYSTEM/DOMAINS/LEGAL_WARFARE/LEGAL_TECH")
from apex_pinecone_indexer import ApexPineconeIndexer, vectorize


def test_pinecone_vectorizer():
    vec = vectorize("Pinecone 1009 Legal Vector Search", dim=1024)
    assert len(vec) == 1024
    assert any(x > 0.0 for x in vec)


def test_pinecone_index_stats():
    stats = ApexPineconeIndexer.get_stats()
    assert "totalVectorCount" in stats or "namespaces" in stats
    assert stats.get("dimension") == 1024 or "dimension" in stats


def test_pinecone_query():
    matches = ApexPineconeIndexer.query("Section 1983 Complaint", top_k=3)
    assert isinstance(matches, list)
    assert len(matches) > 0
    first = matches[0]
    assert "score" in first
    assert "id" in first
