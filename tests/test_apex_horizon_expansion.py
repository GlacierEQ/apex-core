#!/usr/bin/env python3
"""
UNIT TESTS FOR APEX HORIZON ROADMAP EXPANSION (ALL 6 TRACKS)
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from apex_bates_stamper import ApexBatesStamper
from apex_daemon import ApexEstateDaemon
from apex_epistemic_chunker import ApexEpistemicChunker
from apex_repair_loop import ApexRepairLoop
from apex_scrubber import ApexDataScrubber


def test_scrubber_pii_sanitization():
    raw_text = "DOCKET-1FDV-23-0001009 with SSN 123-45-6789 and email agent@apex.org using sk-1234567890abcdef1234567890abcdef"
    clean, counts = ApexDataScrubber.sanitize(raw_text)
    assert "[REDACTED_SSN]" in clean
    assert "[REDACTED_EMAIL]" in clean
    assert "[REDACTED_API_KEY]" in clean
    assert "123-45-6789" not in clean
    assert counts.get("SSN") == 1
    assert counts.get("EMAIL") == 1


def test_multilang_structural_chunking():
    ts_code = """
export interface UserPayload {
    id: string;
    role: string;
}

export function authenticateUser(payload: UserPayload): boolean {
    return payload.role === "admin";
}

export class SessionManager {
    constructor() {}
    public isValid(): boolean {
        return true;
    }
}
"""
    chunks = ApexEpistemicChunker.chunk_multilang_code(ts_code, file_path="auth.ts")
    assert len(chunks) == 3
    types = [c.chunk_type for c in chunks]
    assert "Interface" in types
    assert "Function" in types
    assert "Class" in types
    assert chunks[0].symbols == ["UserPayload"]


def test_bates_stamper_lifecycle(tmp_path):
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()

    (in_dir / "doc1.txt").write_text("Confidential Exhibit A", encoding="utf-8")
    (in_dir / "doc2.txt").write_text("Confidential Exhibit B", encoding="utf-8")

    manifest = ApexBatesStamper.stamp_collection(
        input_dir=in_dir,
        output_dir=out_dir,
        prefix="TEST-",
        start_number=1,
        digits=4
    )

    assert manifest["total_items"] == 2
    assert (out_dir / "BATES_MANIFEST.json").exists()
    assert (out_dir / "BATES_INDEX.md").exists()
    assert (out_dir / "TEST-0001_doc1.txt").exists()
    assert (out_dir / "TEST-0002_doc2.txt").exists()


def test_repair_loop_traceback_parser():
    sample_trace = """
Traceback (most recent call last):
  File "/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts/model_router.py", line 42, in cmd_chat
    res = chat_openrouter(model=args.model)
ZeroDivisionError: division by zero
"""
    res = ApexRepairLoop.extract_failing_file_and_line(sample_trace)
    assert res is not None
    fpath, line_num = res
    assert fpath.name == "model_router.py"
    assert line_num == 42


def test_daemon_health_sweep():
    sweep = ApexEstateDaemon.run_health_sweep()
    assert "hardening" in sweep["checks"]
    assert "mcp_sync" in sweep["checks"]
    assert sweep["healthy"] is True
