#!/usr/bin/env python3
"""
UNIT TESTS FOR APEX MACHINE LEARNING MEMORY ENGINE
Standard: 100% test pass rate for dense vector embedding, cosine similarity, Hebbian reinforcement, and clustering.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from apex_ml_memory_engine import ApexMLMemoryEngine, MemoryNode, _cosine_similarity, _tokenize


def test_tokenizer_and_shingling(tmp_path):
    tokens = _tokenize("APEX Multimodal Model 1.05M")
    assert "apex" in tokens
    assert "multimodal" in tokens
    assert "model" in tokens
    assert len(tokens) > 5  # Includes character shingles


def test_cosine_similarity():
    vec_a = {"ai": 1.0, "agent": 0.8, "code": 0.5}
    vec_b = {"ai": 0.9, "agent": 0.7, "code": 0.6}
    sim = _cosine_similarity(vec_a, vec_b)
    assert sim > 0.90
    assert sim <= 1.0

    vec_disjoint = {"apple": 1.0, "fruit": 0.5}
    assert _cosine_similarity(vec_a, vec_disjoint) == 0.0


def test_ml_memory_lifecycle(tmp_path):
    engine = ApexMLMemoryEngine(store_dir=tmp_path)

    # 1. Add memories
    m1 = engine.add_memory("DeepSeek R1 mathematical reasoning engine and CoT logic", tags=["reasoning", "deepseek"])
    m2 = engine.add_memory("Xiaomi MiMo v2.5 Pro 1.05M multimodal audio video photo analysis", tags=["multimodal", "mimo"])
    m3 = engine.add_memory("Mermicorn workspace isolation from Glacier legal vault", tags=["security", "mermicorn"])

    assert len(engine.nodes) == 3
    assert "MiMo" in m2.entities or "Xiaomi" in m2.entities

    # 2. Semantic Search
    results = engine.semantic_search("Show me audio and video models", limit=2)
    assert len(results) > 0
    top_hit = results[0]
    assert "mimo" in top_hit["content"].lower() or "xiaomi" in top_hit["content"].lower()
    assert top_hit["scoring_breakdown"]["vector_similarity"] > 0
    assert top_hit["access_count"] >= 2

    # 3. Clustering
    clustering = engine.cluster_memories(k=3)
    assert clustering["status"] == "success"
    assert clustering["total_clusters"] > 0

    # 4. Knowledge Graph
    kg = engine.generate_knowledge_graph()
    assert kg["total_nodes"] == 3
    assert isinstance(kg["edges"], list)
