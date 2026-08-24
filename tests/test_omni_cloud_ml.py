#!/usr/bin/env python3
"""
UNIT TESTS FOR APEX OMNI-CLOUD MACHINE LEARNING FILESYSTEM & PERCEPTION ENGINE
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from apex_omni_cloud_ml import ApexOmniCloudMLEngine, CloudDocumentNode, _cosine_similarity, _tokenize


def test_omni_cloud_tokenization():
    tokens = _tokenize("Docket 1FDV-23-0001009 Motion For Summary Judgment")
    assert "docket" in tokens
    assert "motion" in tokens
    assert len(tokens) > 5


def test_omni_cloud_semantic_search_and_graph(tmp_path):
    engine = ApexOmniCloudMLEngine(index_dir=tmp_path)

    # 1. Create simulated multi-cloud documents
    doc1 = CloudDocumentNode(
        doc_id="doc1",
        file_path="/Users/kcbflux/Google Drive/01_LEGAL/Motion_Dismiss.md",
        cloud_source="Google Drive",
        file_name="Motion_Dismiss.md",
        file_size=4096,
        modified_time=1700000000.0,
        content_hash="hash_legal_1",
        text_preview="Motion to Dismiss regarding Docket 1FDV-23-0001009 and evidentiary exhibits.",
        tags=["legal"],
        entities=["DOCKET:1FDV-23-0001009", "Dismiss", "Motion"],
    )
    doc2 = CloudDocumentNode(
        doc_id="doc2",
        file_path="/Users/kcbflux/Dropbox-Cyber.lazer.mermicor/takeout/manifest.json",
        cloud_source="Dropbox (Mermicorn)",
        file_name="manifest.json",
        file_size=2048,
        modified_time=1700000100.0,
        content_hash="hash_mermi_2",
        text_preview="Camera uploads and photo metadata timeline for 2026-08-24.",
        tags=["multimedia", "mermicorn"],
        entities=["Camera", "Uploads", "DATE:2026-08-24"],
    )

    engine.docs[doc1.doc_id] = doc1
    engine.docs[doc2.doc_id] = doc2
    engine._rebuild_doc_frequencies()

    # 2. Test Cross-Cloud Semantic Search
    results = engine.semantic_search("Find court motions and docket entries")
    assert len(results) > 0
    assert results[0]["file_name"] == "Motion_Dismiss.md"
    assert results[0]["cloud_source"] == "Google Drive"

    # 3. Test Clustering
    clusters = engine.cluster_documents(k=6)
    assert clusters["total_clusters"] > 0

    # 4. Test Cross-Cloud Graph
    graph = engine.generate_cross_cloud_graph()
    assert graph["total_nodes"] == 2
