#!/usr/bin/env python3
"""
UNIT TESTS FOR APPLE SILICON HARDWARE VECTOR ACCELERATION ENGINE
"""

import sys
from pathlib import Path

# Add scripts directory
sys.path.insert(0, "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts")
from apex_ml_metal_engine import AppleHardwareVectorEngine


def test_text_to_embedding_normalization():
    text = "APEX Omniversal Holographic Mesh"
    vec, c_arr = AppleHardwareVectorEngine.text_to_embedding(text, dim=512)
    assert len(vec) == 512
    # Verify L2 unit norm
    l2_sum = sum(x * x for x in vec)
    assert abs(l2_sum - 1.0) < 1e-4


def test_hardware_dot_product_identity():
    engine = AppleHardwareVectorEngine()
    v1, a1 = AppleHardwareVectorEngine.text_to_embedding("Identical text query", dim=256)
    if engine.has_accelerate and engine.cblas_sdot:
        score = float(engine.cblas_sdot(256, a1, 1, a1, 1))
        assert abs(score - 1.0) < 1e-4


def test_hardware_benchmark_execution():
    res = AppleHardwareVectorEngine.benchmark_hardware(iterations=100, dim=256)
    assert res["iterations"] == 100
    assert res["avg_latency_microseconds"] > 0
    assert res["throughput_vector_ops_per_sec"] > 0


def test_similarity_query():
    engine = AppleHardwareVectorEngine()
    res = engine.query_similarity("forensic evidence timeline", top_k=5)
    assert "query" in res
    assert "elapsed_ms" in res
    assert "matches" in res
