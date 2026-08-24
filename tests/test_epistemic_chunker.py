#!/usr/bin/env python3
"""
UNIT TESTS FOR APEX ELITE EPISTEMIC & CHUNK POWER ENGINE
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from apex_epistemic_chunker import ApexEpistemicChunker, EpistemicLayer


def test_epistemic_layer_audit(tmp_path):
    # 1. Non-existent file (L0 Failure)
    non_existent = tmp_path / "ghost.py"
    r0 = ApexEpistemicChunker.audit_epistemic_layer(non_existent)
    assert not r0.is_valid
    assert r0.layer_achieved == EpistemicLayer.L0_PRESENCE

    # 2. Valid Syntax File (L1 Success)
    valid_file = tmp_path / "valid.py"
    valid_file.write_text("def calculate_power(x: int) -> int:\n    return x * x\n", encoding="utf-8")
    r1 = ApexEpistemicChunker.audit_epistemic_layer(valid_file)
    assert r1.is_valid
    assert r1.layer_achieved == EpistemicLayer.L1_STRUCTURE
    assert "calculate_power" in r1.details["symbols"]

    # 3. Behavioral Test (L2 Success)
    r2 = ApexEpistemicChunker.audit_epistemic_layer(
        valid_file,
        test_command=f"python3 -c 'from valid import calculate_power; assert calculate_power(4) == 16'"
    )
    # Pythonpath resolution for tmp_path test
    import os
    env_test = f"PYTHONPATH={tmp_path} python3 -c 'from valid import calculate_power; assert calculate_power(4) == 16'"
    r2 = ApexEpistemicChunker.audit_epistemic_layer(valid_file, test_command=env_test)
    assert r2.is_valid
    assert r2.layer_achieved == EpistemicLayer.L2_BEHAVIOR


def test_syntax_aware_ast_chunking():
    sample_code = """
def alpha():
    x = 1
    return x

class BetaEngine:
    def __init__(self):
        self.state = True
        
    def execute(self):
        return 42
"""
    chunks = ApexEpistemicChunker.chunk_python_code(sample_code, file_path="test_module.py")
    assert len(chunks) == 2
    assert chunks[0].chunk_type == "FunctionDef"
    assert chunks[0].symbols == ["alpha"]
    assert chunks[1].chunk_type == "ClassDef"
    assert chunks[1].symbols == ["BetaEngine"]
    assert len(chunks[0].content_hash) == 12


def test_linear_text_chunking():
    doc = "\n".join([f"Line {i}: Evidence data point for docket." for i in range(1, 101)])
    chunks = ApexEpistemicChunker.chunk_text_linear(doc, file_path="evidence.txt", max_lines=40, overlap_lines=10)
    assert len(chunks) >= 3
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 40
