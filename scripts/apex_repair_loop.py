#!/usr/bin/env python3
"""
APEX CLOSED-LOOP TEST & AUTO-REPAIR DAEMON
Standard: Closed-loop iterative execution: Run -> Parse Trace -> Extract AST Chunk -> AI Repair -> Verify Green.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

GATEWAY_PATH = Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/MCP_SERVERS/openrouter-free-gateway")
if str(GATEWAY_PATH) not in sys.path:
    sys.path.insert(0, str(GATEWAY_PATH))

SCRIPTS_PATH = Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/apex-core/scripts")
if str(SCRIPTS_PATH) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_PATH))

from apex_epistemic_chunker import ApexEpistemicChunker
from server import chat_openrouter


class ApexRepairLoop:
    """
    Automates test execution, error extraction, and closed-loop code repair.
    """

    @staticmethod
    def run_command(cmd: str, cwd: Optional[str] = None) -> Tuple[int, str, str]:
        p = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
        )
        return p.returncode, p.stdout, p.stderr

    @staticmethod
    def extract_failing_file_and_line(trace: str) -> Optional[Tuple[Path, int]]:
        # Match Python tracebacks: File "/path/to/file.py", line 123
        py_match = re.findall(r'File "([^"]+)", line (\d+)', trace)
        if py_match:
            # Pick last user file
            for fpath, lnum in reversed(py_match):
                p = Path(fpath)
                if p.exists() and "site-packages" not in str(p) and "lib/python" not in str(p):
                    return p, int(lnum)

        # Match generic errors: path/to/file.ts:123:45 or file.go:123
        gen_match = re.findall(r'([a-zA-Z0-9_\-\.\/]+\.[a-zA-Z0-9]+):(\d+)', trace)
        if gen_match:
            for fpath, lnum in reversed(gen_match):
                p = Path(fpath)
                if p.exists():
                    return p, int(lnum)

        return None

    @classmethod
    def execute_repair_loop(
        cls,
        test_command: str,
        max_attempts: int = 3,
        cwd: Optional[str] = None,
    ) -> bool:
        print("=" * 80)
        print("🔧 APEX CLOSED-LOOP TEST & REPAIR DAEMON INITIATED")
        print(f"Command: {test_command}")
        print("=" * 80)

        for attempt in range(1, max_attempts + 1):
            print(f"\n[*] [Iteration {attempt}/{max_attempts}] Executing verification test...")
            ret, stdout, stderr = cls.run_command(test_command, cwd=cwd)

            if ret == 0:
                print("=" * 80)
                print(f"🟢 VERIFICATION PASSED: 100% GREEN ON ATTEMPT {attempt}")
                print("=" * 80)
                return True

            print(f"⚠️ Test failed (Exit code {ret}). Parsing stack trace...")
            combined_err = f"{stdout}\n{stderr}"
            target_info = cls.extract_failing_file_and_line(combined_err)

            if not target_info:
                print("❌ Could not isolate specific source file from error output.")
                print(combined_err[:500])
                return False

            target_file, line_num = target_info
            print(f"  └─ Isolated defect in: {target_file} (Line {line_num})")

            file_content = target_file.read_text(encoding="utf-8")
            chunks = ApexEpistemicChunker.chunk_multilang_code(file_content, file_path=str(target_file))

            # Find matching chunk
            target_chunk = None
            for c in chunks:
                if c.start_line <= line_num <= c.end_line:
                    target_chunk = c
                    break
            if not target_chunk:
                target_chunk = chunks[0] if chunks else None

            if not target_chunk:
                print("❌ Could not extract target AST code chunk.")
                return False

            print(f"  └─ Extracted AST Chunk: [{target_chunk.chunk_id}] (Lines {target_chunk.start_line}-{target_chunk.end_line})")

            # Dispatch to AI Repair Engine
            repair_prompt = f"""You are an automated code repair engine. Fix the defect in the code chunk below.

Failing Test Command: {test_command}
Error Output:
{combined_err[:600]}

Target File: {target_file} (Lines {target_chunk.start_line}-{target_chunk.end_line})
Original Code Chunk:
```
{target_chunk.content}
```

Return ONLY the complete, corrected replacement code for this chunk. No explanations, no markdown formatting if possible."""

            print("  [*] Dispatching chunk to AI Repair Engine (Poolside Laguna S 2.1)...")
            res = chat_openrouter(
                model="poolside/laguna-s-2.1:free",
                prompt=repair_prompt,
                max_tokens=2048,
                temperature=0.1,
            )

            if res.get("status") != "success":
                print(f"❌ AI repair call failed: {res.get('message')}")
                return False

            repaired_code = res.get("response", "").strip()
            # Clean markdown code blocks if model wrapped them
            if repaired_code.startswith("```"):
                repaired_code = re.sub(r"^```[a-zA-Z]*\n", "", repaired_code)
                repaired_code = re.sub(r"\n```$", "", repaired_code)

            # Apply replacement in file
            all_lines = file_content.splitlines(keepends=True)
            before = "".join(all_lines[: target_chunk.start_line - 1])
            after = "".join(all_lines[target_chunk.end_line :])
            new_file_content = before + repaired_code + ("\n" if not repaired_code.endswith("\n") else "") + after

            target_file.write_text(new_file_content, encoding="utf-8")
            print(f"  ✓ Applied repair patch to {target_file}. Re-verifying...")

        print("\n❌ Max repair attempts exceeded without reaching 100% green.")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="APEX Closed-Loop Test & Auto-Repair Daemon")
    parser.add_argument("cmd", help="Test command to run and verify (e.g. 'pytest tests/')")
    parser.add_argument("--max-attempts", "-m", type=int, default=3, help="Max repair iterations")
    args = parser.parse_args()

    success = ApexRepairLoop.execute_repair_loop(args.cmd, max_attempts=args.max_attempts)
    sys.exit(0 if success else 1)
